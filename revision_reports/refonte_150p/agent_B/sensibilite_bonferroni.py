import csv, statistics, sys
from scipy.stats import t
B="experiments/phase_revision_20261105/"
def load(d): return list(csv.DictReader(open(B+d+"/runs.csv",encoding="utf-8")))
def ci(v,alpha):
    n=len(v);m=statistics.fmean(v);h=t.ppf(1-alpha/2,n-1)*statistics.stdev(v)/n**.5;return m-h,m+h
def contrast(rows,sc,arm,ref,w,alpha):
    a={r["seed"]:r for r in rows if r["scenario"]==sc and r["arm"]==arm and r["workers"]==w}
    b={r["seed"]:r for r in rows if r["scenario"]==sc and r["arm"]==ref and r["workers"]==w}
    s=sorted(a)
    fd=[float(a[k]["first_execution_failure_rate"])-float(b[k]["first_execution_failure_rate"]) for k in s]
    rr=[float(a[k]["throughput_tasks_sec"])/float(b[k]["throughput_tasks_sec"]) for k in s]
    return ci(fd,alpha),ci(rr,alpha)
def dec_cnp(f,r):
    if (f[1]<0 and r[0]>=0.95) or (r[0]>1.05 and f[1]<=0.01): return "favorable"
    if f[0]>0 or (r[1]<0.95 and f[1]>=0): return "defavorable"
    return "indetermine"
rows=load("E-H5-MEMORY-RELIABILITY")
for alpha in (0.05,0.05/3):
    print("E-H5 alpha",round(alpha,4),[ (p, (lambda f,r: f[1]<0 and r[0]>=0.95)(*contrast(rows,f"best_declared_failure_p{p}","D","C","3",alpha))) for p in ("30","60","90")])
rows=load("E-CNP-STATIC-ASSIGNMENT")
sc=["s1_nominal","s2_best_declared_failure_p30","s3_silent_gamma_failure","s4_slow_gamma"]
for alpha in (0.05,0.05/8):
    print("E-CNP alpha",round(alpha,4),[(s[:2],arm,dec_cnp(*contrast(rows,s,arm,"static","3",alpha))) for s in sc for arm in ("C","D")])
rows=load("E-CNP-LEAST-LOADED")
for alpha in (0.05,0.05/4,0.05/12):
    print("LL alpha",round(alpha,4),[(s[:2],dec_cnp(*contrast(rows,s,"C","least_loaded","3",alpha))) for s in sc])
    print("   C-static",[(s[:2],dec_cnp(*contrast(rows,s,"C","static","3",alpha))) for s in sc], "LL-static",[(s[:2],dec_cnp(*contrast(rows,s,"least_loaded","static","3",alpha))) for s in sc])
