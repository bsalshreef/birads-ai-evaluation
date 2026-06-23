"""
Final Corrected Analysis — Revision 2
Fixes all remaining reviewer issues:
1. BI-RADS DCA: use BI-RADS-derived continuous probability (logistic model) so it
   behaves as a smooth curve, not a step function with impossible constant values.
2. Subgroup NB: standardise ALL subgroup NB to overall cohort denominator (N=5000).
3. Brier scores: verify AI scores are in [0,1]; report alongside null model.
4. Remove max-NB statement; replace with threshold-specific max.
5. Complete Table 5 (Combined biopsy row, FP values).
"""

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.metrics import (roc_auc_score, average_precision_score,
                              roc_curve, confusion_matrix)
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import OneHotEncoder
from sklearn.calibration import calibration_curve
import json, warnings
warnings.filterwarnings('ignore')

np.random.seed(42)

# ── Load data ──────────────────────────────────────────────────
df = pd.read_csv('/home/ubuntu/birads_study/data/vindr_simulated.csv')
y      = df['cancer_outcome'].values
ai     = df['ai_score'].values
birads = df['birads'].values
density= df['density'].values
age    = df['age'].values
lesion = df['lesion_type'].values
N      = len(df)
prev   = y.mean()
print(f"N={N}, Cancers={y.sum()}, Prevalence={prev*100:.2f}%")
print(f"AI score range: [{ai.min():.4f}, {ai.max():.4f}]  (must be in [0,1])")

# ── Strategies ─────────────────────────────────────────────────
birads_score = birads.astype(float)

enc = OneHotEncoder(sparse_output=False, drop='first')
birads_dummies = enc.fit_transform(birads.reshape(-1,1))
X_combined = np.hstack([birads_dummies, ai.reshape(-1,1)])
lr_comb = LogisticRegression(max_iter=1000, random_state=42)
lr_comb.fit(X_combined, y)
combined_score = lr_comb.predict_proba(X_combined)[:,1]

# BI-RADS as a calibrated probability model (logistic on birads integer)
lr_birads = LogisticRegression(max_iter=1000, random_state=42)
lr_birads.fit(birads_score.reshape(-1,1), y)
birads_prob = lr_birads.predict_proba(birads_score.reshape(-1,1))[:,1]
print(f"BI-RADS prob range: [{birads_prob.min():.4f}, {birads_prob.max():.4f}]")

density_dummies = enc.fit_transform(density.reshape(-1,1))
X_base = np.hstack([age.reshape(-1,1), density_dummies])
lr_base = LogisticRegression(max_iter=1000, random_state=42)
lr_base.fit(X_base, y)
baseline_score = lr_base.predict_proba(X_base)[:,1]

# ── Stratified bootstrap ────────────────────────────────────────
def strat_boot_ci(func, y, score, n_boot=2000):
    pos = np.where(y==1)[0]; neg = np.where(y==0)[0]
    vals = []
    for _ in range(n_boot):
        idx = np.concatenate([np.random.choice(pos, len(pos), replace=True),
                              np.random.choice(neg, len(neg), replace=True)])
        try: vals.append(func(y[idx], score[idx]))
        except: pass
    return round(np.percentile(vals, 2.5), 3), round(np.percentile(vals, 97.5), 3)

# ── 1. DISCRIMINATION ───────────────────────────────────────────
disc = {}
for name, sc in [('birads', birads_prob), ('ai', ai),
                 ('combined', combined_score), ('baseline', baseline_score)]:
    auc_v = round(roc_auc_score(y, sc), 3)
    pr_v  = round(average_precision_score(y, sc), 3)
    al, ah = strat_boot_ci(roc_auc_score, y, sc)
    pl, ph = strat_boot_ci(average_precision_score, y, sc)
    disc[name] = dict(auc=auc_v, auc_lo=al, auc_hi=ah,
                      pr_auc=pr_v, pr_lo=pl, pr_hi=ph)
    print(f"  {name}: AUC={auc_v}({al}–{ah}), PR-AUC={pr_v}({pl}–{ph})")

# ── 2. BRIER SCORES ─────────────────────────────────────────────
def brier(y, sc): return float(np.mean((sc - y)**2))

null_b = brier(y, np.full(N, prev))
ai_b   = brier(y, ai)
comb_b = brier(y, combined_score)
bir_b  = brier(y, birads_prob)

# Platt recalibration
lo_ai = np.log(ai.clip(1e-6,1-1e-6)/(1-ai.clip(1e-6,1-1e-6)))
lr_recal = LogisticRegression(max_iter=1000)
lr_recal.fit(lo_ai.reshape(-1,1), y)
ai_recal = lr_recal.predict_proba(lo_ai.reshape(-1,1))[:,1]
recal_b = brier(y, ai_recal)

print(f"\nBrier: null={null_b:.6f}, AI={ai_b:.6f}, AI-recal={recal_b:.6f}, "
      f"Combined={comb_b:.6f}, BI-RADS-prob={bir_b:.6f}")

# Subgroup Brier — check against subgroup null
def subgroup_brier_check(mask, sc, y):
    yy = y[mask]; ss = sc[mask]
    b = brier(yy, ss)
    null_b = brier(yy, np.full(len(yy), yy.mean()))
    return round(b, 6), round(null_b, 6)

print("\nSubgroup Brier vs null:")
for b_cat in [3,4,5]:
    mask = birads == b_cat
    b_val, n_val = subgroup_brier_check(mask, ai, y)
    print(f"  BI-RADS {b_cat} (prev={y[mask].mean()*100:.1f}%): Brier={b_val}, null={n_val}")

# ── 3. CALIBRATION ──────────────────────────────────────────────
def cal_metrics(sc, y, n_bins=10):
    b = brier(y, sc)
    bins = np.linspace(0,1,n_bins+1)
    ece = sum(mask.sum()/len(y)*abs(sc[mask].mean()-y[mask].mean())
              for i in range(n_bins)
              for mask in [(sc>=bins[i])&(sc<bins[i+1])] if mask.sum()>0)
    lo = np.log(sc.clip(1e-6,1-1e-6)/(1-sc.clip(1e-6,1-1e-6)))
    lr = LogisticRegression(max_iter=1000)
    try:
        lr.fit(lo.reshape(-1,1), y)
        intc = round(lr.intercept_[0], 3)
        slp  = round(lr.coef_[0][0], 3)
    except: intc, slp = None, None
    return dict(brier=round(b,6), ece=round(ece,4), intercept=intc, slope=slp)

cal_overall = cal_metrics(ai, y)
cal_birads  = {b: cal_metrics(ai[birads==b], y[birads==b])
               if (birads==b).sum()>10 and 0<y[birads==b].sum()<(birads==b).sum()
               else None for b in [1,2,3,4,5]}
cal_density = {d: cal_metrics(ai[density==d], y[density==d])
               if (density==d).sum()>10 and 0<y[density==d].sum()<(density==d).sum()
               else None for d in ['A','B','C','D']}

print(f"\nCalibration overall: {cal_overall}")

# ── 4. OPERATING POINTS ─────────────────────────────────────────
def op_pt(sc, y, thresh):
    pred = (sc>=thresh).astype(int)
    tn,fp,fn,tp = confusion_matrix(y, pred, labels=[0,1]).ravel()
    n = len(y)
    sens = tp/(tp+fn) if tp+fn>0 else 0
    cdr  = tp/n*1000
    fp_k = fp/n*1000
    fp_c = fp/tp if tp>0 else float('inf')
    return dict(sens=round(sens,3), cdr=round(cdr,1), fp_k=round(fp_k,1),
                fp_c=round(fp_c,1), tp=int(tp), fp=int(fp), tn=int(tn), fn=int(fn),
                recall_pct=round((tp+fp)/n*100,1))

birads_recall_rate  = (birads>=3).mean()
birads_biopsy_rate  = (birads>=4).mean()
bir_recall  = op_pt(birads_prob, y, np.percentile(birads_prob, (1-birads_recall_rate)*100))
bir_biopsy  = op_pt(birads_prob, y, np.percentile(birads_prob, (1-birads_biopsy_rate)*100))
ai_recall   = op_pt(ai, y, np.percentile(ai,  (1-birads_recall_rate)*100))
ai_biopsy   = op_pt(ai, y, np.percentile(ai,  (1-birads_biopsy_rate)*100))
comb_recall = op_pt(combined_score, y, np.percentile(combined_score, (1-birads_recall_rate)*100))
comb_biopsy = op_pt(combined_score, y, np.percentile(combined_score, (1-birads_biopsy_rate)*100))

print(f"\nOperating points (recall rate {birads_recall_rate*100:.1f}%):")
print(f"  BI-RADS: sens={bir_recall['sens']}, CDR={bir_recall['cdr']}, FP/k={bir_recall['fp_k']}")
print(f"  AI:      sens={ai_recall['sens']},  CDR={ai_recall['cdr']},  FP/k={ai_recall['fp_k']}")
print(f"  Combined:sens={comb_recall['sens']}, CDR={comb_recall['cdr']}, FP/k={comb_recall['fp_k']}")

# ── 5. DCA — CORRECTED (all continuous probability scores) ──────
# Use birads_prob (logistic model) so BI-RADS is a smooth curve.
def nb(y, sc, pt):
    pred = (sc>=pt).astype(int)
    tn,fp,fn,tp = confusion_matrix(y, pred, labels=[0,1]).ravel()
    return tp/len(y) - fp/len(y)*(pt/(1-pt))

thresholds = np.arange(0.01, 0.31, 0.005)
nb_bir  = np.array([nb(y, birads_prob, t) for t in thresholds])*1000
nb_ai   = np.array([nb(y, ai,          t) for t in thresholds])*1000
nb_comb = np.array([nb(y, combined_score, t) for t in thresholds])*1000
nb_all  = np.array([prev - (1-prev)*t/(1-t) for t in thresholds])*1000
nb_none = np.zeros(len(thresholds))

# Summary at key thresholds
dca_sum = {}
for tk in [0.02, 0.05, 0.10, 0.15]:
    idx = np.argmin(np.abs(thresholds - tk))
    dca_sum[tk] = dict(birads=round(nb_bir[idx],3), ai=round(nb_ai[idx],3),
                       combined=round(nb_comb[idx],3), treat_all=round(nb_all[idx],3))

print("\nDCA summary (per 1000, all continuous probability models):")
for tk, v in dca_sum.items():
    max_nb = round(prev*1000*(1-tk)/tk, 1) if tk < 1 else 0  # theoretical max
    print(f"  {tk*100:.0f}%: BI-RADS={v['birads']}, AI={v['ai']}, "
          f"Combined={v['combined']}, Treat-all={v['treat_all']}, "
          f"Max-possible={max_nb}")

# ── 6. SUBGROUP ANALYSIS — overall denominator ──────────────────
# NB is always computed with y and sc for the subgroup, but expressed
# per 1000 OVERALL women (divide by N, not subgroup n).
def nb_overall_denom(y_sub, sc_sub, pt, N_overall):
    """NB using overall cohort denominator."""
    pred = (sc_sub >= pt).astype(int)
    tn,fp,fn,tp = confusion_matrix(y_sub, pred, labels=[0,1]).ravel()
    return (tp/N_overall - fp/N_overall*(pt/(1-pt)))*1000

def subgroup_full(mask, sc, y, name, N_overall, n_boot=2000):
    yy, ss = y[mask], sc[mask]
    if yy.sum()<2 or yy.sum()==len(yy): 
        return dict(name=name, n=int(mask.sum()))
    try: auc_v = round(roc_auc_score(yy, ss), 3)
    except: auc_v = None
    brier_v = round(brier(yy, ss), 6)
    null_brier_v = round(brier(yy, np.full(len(yy), yy.mean())), 6)
    nb5 = round(nb_overall_denom(yy, ss, 0.05, N_overall), 3)
    # CI for AUC
    pos=np.where(yy==1)[0]; neg=np.where(yy==0)[0]
    auc_boots=[]
    for _ in range(n_boot):
        if len(pos)<1 or len(neg)<1: break
        idx=np.concatenate([np.random.choice(pos,len(pos),replace=True),
                            np.random.choice(neg,len(neg),replace=True)])
        try: auc_boots.append(roc_auc_score(yy[idx], ss[idx]))
        except: pass
    auc_lo = round(np.percentile(auc_boots,2.5),3) if auc_boots else None
    auc_hi = round(np.percentile(auc_boots,97.5),3) if auc_boots else None
    # FP at 90% sens
    try:
        fpr_s,tpr_s,thr_s = roc_curve(yy, ss)
        idx90 = np.where(tpr_s>=0.90)[0]
        if len(idx90)>0:
            t90 = thr_s[idx90[0]]
            pred90=(ss>=t90).astype(int)
            tn90,fp90,fn90,tp90=confusion_matrix(yy,pred90,labels=[0,1]).ravel()
            fp90_v = round(fp90/N_overall*1000, 2)
        else: fp90_v = None
    except: fp90_v = None
    return dict(name=name, n=int(mask.sum()), auc=auc_v, auc_lo=auc_lo, auc_hi=auc_hi,
                brier=brier_v, null_brier=null_brier_v, nb_5pct=nb5, fp_90=fp90_v)

subgroups = {}
subgroups['age_lt50']   = subgroup_full(age<50, ai, y, 'Age <50', N)
subgroups['age_50_69']  = subgroup_full((age>=50)&(age<70), ai, y, 'Age 50–69', N)
subgroups['age_ge70']   = subgroup_full(age>=70, ai, y, 'Age ≥70†', N)
for d in ['A','B','C','D']:
    subgroups[f'dens_{d}'] = subgroup_full(density==d, ai, y, f'Density {d}', N)
for b in [3,4,5]:
    subgroups[f'bir_{b}'] = subgroup_full(birads==b, ai, y, f'BI-RADS {b}', N)
for lt in ['Mass','Calcification','Architectural Distortion','Focal Asymmetry']:
    k = lt.lower().replace(' ','_')
    subgroups[k] = subgroup_full(lesion==lt, ai, y, lt, N)

print("\nSubgroup NB (per 1000 OVERALL women):")
for k,v in subgroups.items():
    if 'auc' in v and v['auc'] is not None:
        print(f"  {v['name']}: n={v['n']}, AUC={v['auc']}({v['auc_lo']}–{v['auc_hi']}), "
              f"Brier={v['brier']} (null={v['null_brier']}), NB@5%={v['nb_5pct']}/1000")

# ── 7. FIGURES ──────────────────────────────────────────────────
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,
                     'axes.titlesize':13,'axes.labelsize':12,
                     'xtick.labelsize':10,'ytick.labelsize':10,
                     'legend.fontsize':10,'figure.dpi':150,
                     'axes.spines.top':False,'axes.spines.right':False})
C = {'birads':'#2166AC','ai':'#D6604D','combined':'#1A9641',
     'treat_all':'#666666','treat_none':'#AAAAAA'}

# Figure 6: DCA (corrected)
fig, ax = plt.subplots(figsize=(10,6))
ax.plot(thresholds*100, nb_bir,  color=C['birads'],    lw=2.5, label='BI-RADS (logistic)')
ax.plot(thresholds*100, nb_ai,   color=C['ai'],        lw=2.5, label='AI alone')
ax.plot(thresholds*100, nb_comb, color=C['combined'],  lw=2.5, label='Combined BI-RADS+AI')
ax.plot(thresholds*100, nb_all,  color=C['treat_all'], lw=1.5, ls='--', label='Treat all')
ax.axhline(0, color=C['treat_none'], lw=1.5, ls=':', label='Treat none')
sup = nb_comb > nb_bir
ax.fill_between(thresholds*100, nb_bir, nb_comb, where=sup,
                alpha=0.15, color=C['combined'], label='Combined superior')
ax.set_xlabel('Threshold Probability (%)')
ax.set_ylabel('Net Benefit (per 1,000 women)')
ax.set_title('Figure 6. Decision Curve Analysis (Final Corrected)')
ax.legend(loc='upper right', fontsize=9)
ax.set_xlim(1,30); ax.set_ylim(-5,35); ax.grid(True,alpha=0.3)
fig.tight_layout()
fig.savefig('/home/ubuntu/birads_study/figures/fig5_dca_final.png', dpi=150, bbox_inches='tight')
plt.close()
print("\nDCA figure saved")

# Figure 7: Subgroup heatmap (corrected NB, overall denominator)
sg_plot = [
    ('Age <50',       age<50),
    ('Age 50–69',     (age>=50)&(age<70)),
    ('Age ≥70†',      age>=70),
    ('Density A',     density=='A'),
    ('Density B',     density=='B'),
    ('Density C',     density=='C'),
    ('Density D',     density=='D'),
    ('Mass',          lesion=='Mass'),
    ('Calcification', lesion=='Calcification'),
    ('Focal Asymmetry',lesion=='Focal Asymmetry'),
]
hdata, rlabels = [], []
for name, mask in sg_plot:
    yy, ss = y[mask], ai[mask]
    if yy.sum()<2 or yy.sum()==len(yy): continue
    rlabels.append(name)
    try: auc_v = roc_auc_score(yy, ss)
    except: auc_v = np.nan
    brier_v = brier(yy, ss)
    nb5 = nb_overall_denom(yy, ss, 0.05, N)
    try:
        _,tpr_s,thr_s = roc_curve(yy, ss)
        idx90 = np.where(tpr_s>=0.90)[0]
        if len(idx90)>0:
            pred90=(ss>=thr_s[idx90[0]]).astype(int)
            _,fp90,_,_ = confusion_matrix(yy,pred90,labels=[0,1]).ravel()
            fp90_v = fp90/N*1000
        else: fp90_v = np.nan
    except: fp90_v = np.nan
    hdata.append([auc_v, brier_v, nb5, fp90_v])

harr = np.array(hdata, dtype=float)
def norm_col(col, hib=True):
    v = col[~np.isnan(col)]
    if len(v)==0: return col
    mn,mx = v.min(),v.max()
    if mx==mn: return np.full_like(col,0.5)
    n = (col-mn)/(mx-mn)
    return n if hib else 1-n

norm = np.column_stack([norm_col(harr[:,0],True), norm_col(harr[:,1],False),
                        norm_col(harr[:,2],True), norm_col(harr[:,3],False)])
fig2,ax2 = plt.subplots(figsize=(11,7))
im = ax2.imshow(norm, cmap=plt.cm.RdYlGn, aspect='auto', vmin=0, vmax=1)
fmts = [lambda v:f'{v:.3f}', lambda v:f'{v:.4f}',
        lambda v:f'{v:.3f}', lambda v:f'{v:.2f}']
for i in range(len(rlabels)):
    for j in range(4):
        val = harr[i,j]
        if not np.isnan(val):
            ax2.text(j,i,fmts[j](val),ha='center',va='center',
                     fontsize=9,fontweight='bold',color='#111111')
ax2.set_xticks(range(4))
ax2.set_xticklabels(['AUC','Brier\nScore','Net Benefit\n@5% (/1000 overall)','FP/1000\n@90% Sens'],fontsize=10)
ax2.set_yticks(range(len(rlabels))); ax2.set_yticklabels(rlabels,fontsize=10)
ax2.set_title('Figure 7. Subgroup Equity Heatmap\n'
              '(NB per 1,000 overall women; † Age ≥70: exploratory, n=105)',
              fontsize=12,fontweight='bold')
fig2.colorbar(im,ax=ax2,fraction=0.03,pad=0.04).set_label('Relative Performance',fontsize=9)
fig2.tight_layout()
fig2.savefig('/home/ubuntu/birads_study/figures/fig6_heatmap_final.png', dpi=150, bbox_inches='tight')
plt.close()
print("Heatmap figure saved")

# ── Save results ────────────────────────────────────────────────
def conv(o):
    if isinstance(o,(np.integer,)): return int(o)
    if isinstance(o,(np.floating,)): return float(o)
    if isinstance(o,np.ndarray): return o.tolist()
    if isinstance(o,dict): return {k:conv(v) for k,v in o.items()}
    if isinstance(o,list): return [conv(i) for i in o]
    return o

final = dict(
    discrimination=disc,
    brier=dict(null=round(null_b,6), ai=round(ai_b,6), ai_recal=round(recal_b,6),
               combined=round(comb_b,6), birads_prob=round(bir_b,6)),
    calibration=dict(overall=cal_overall, by_birads=cal_birads, by_density=cal_density),
    operating_points=dict(
        recall_rate_pct=round(birads_recall_rate*100,1),
        biopsy_rate_pct=round(birads_biopsy_rate*100,2),
        birads_recall=bir_recall, ai_recall=ai_recall, comb_recall=comb_recall,
        birads_biopsy=bir_biopsy, ai_biopsy=ai_biopsy, comb_biopsy=comb_biopsy),
    dca=dict(thresholds=thresholds.tolist(),
             nb_birads=nb_bir.tolist(), nb_ai=nb_ai.tolist(),
             nb_combined=nb_comb.tolist(), nb_treat_all=nb_all.tolist(),
             summary=dca_sum),
    subgroups=subgroups,
)
with open('/home/ubuntu/birads_study/results/final_results.json','w') as f:
    json.dump(conv(final), f, indent=2)
print("\n✓ Final results saved to results/final_results.json")
