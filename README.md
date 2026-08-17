Algorithm: Multi-Agent Security Evaluation
==========================================
Require:
    - Configuration list C = {B1_unhardened, B2_best_practice, B3_ARGUS}
    - Attack corpus A = {a_1, a_2, ..., a_N}, N ≈ 450
    - Number of trials T = 30
    - Function HUMAN_RATERS(output) → (r1,r2,r3) ∈ {1..5}^3

Ensure:
    - Trial results R[c][a] = list of metric dicts per trial
    - Krippendorff's α across all auditability scores
    - For each scalar metric m:
        - Adjusted p-values for Wilcoxon tests on config pairs
        - Cliff's δ effect sizes
        - Holm-Bonferroni significance flags

1:  procedure RUN_EXPERIMENT(C, A, T)
2:      R ← {}  // results dictionary
3:      all_audit_ratings ← []
4:
5:      for each config c ∈ C do
6:          for each attack a ∈ A do
7:              trial_scores ← []
8:              for t ← 1 to T do
9:                  seed ← RANDOM(0, 999999)
10:                 rng ← RANDOM_GENERATOR(seed)
11:
12:                 //  Testbed initialisation
13:                 INIT_AGENTS(c.frameworks, c.models, seed)  // TODO: real init
14:                 START_MCP_SERVERS(a.tools_involved, seed)
15:
16:                 //  Attack execution & metric collection
17:                 outcome ← EXECUTE_ATTACK(a.prompt, a.target_agent, c)
18:                 asr ← outcome.success ? 1 : 0
19:                 plr ← outcome.pii_leaked ? 1 : 0
20:                 tu ← BENIGN_TASK_SUCCESS(c) ? 1 : 0
21:                 latencies ← outcome.message_latencies  // list of ms
22:                 trust_rounds ← TRUST_CONVERGENCE(c, a) // integer
23:                 ratings ← HUMAN_RATERS(outcome.output) // 3 integers
24:
25:                 metrics ← {ASR: asr, PLR: plr, TU: tu,
26:                            latencies: latencies,
27:                            trust_rounds: trust_rounds,
28:                            auditability_ratings: ratings}
29:                 trial_scores.append(metrics)
30:                 all_audit_ratings.append(ratings)
31:             end for
32:             R[(c, a.id)] ← trial_scores
33:         end for
34:     end for
35:     return R, all_audit_ratings
36: end procedure
37:
38: procedure KRIPPENDORFF_ALPHA(all_ratings)
39:     data ← TRANSPOSE(all_ratings)   // shape (3, N_items)
40:     α ← krippendorff.alpha(data, level='ordinal')
41:     return α
42: end procedure
43:
44: procedure STATISTICAL_TESTS(R, attack_ids, config_pairs, metric_key)
45:     p_vals ← [], δ_vals ← [], test_ids ← []
46:     for each a ∈ attack_ids do
47:         for each (c1, c2) ∈ config_pairs do
48:             x ← [trial[metric_key] for trial in R[(c1, a)]]
49:             y ← [trial[metric_key] for trial in R[(c2, a)]]
50:             _, p ← WILCOXON(x, y)          // paired
51:             δ ← CLIFF_DELTA(y, x)          // positive = c2 improves over c1
52:             p_vals.append(p)
53:             δ_vals.append(δ)
54:             test_ids.append((a, c1, c2))
55:         end for
56:     end for
57:     reject, adj_p, _, _ ← HOLM_BONFERRONI(p_vals, α=0.05)
58:     return test_ids, adj_p, δ_vals, reject
59: end procedure
60:
61: //  Main
62: C ← {B1, B2, B3}
63: A ← GENERATE_ATTACK_CORPUS(50 per category)   // ≈ 450 attacks
64: R, audit_data ← RUN_EXPERIMENT(C, A, T=30)
65: α ← KRIPPENDORFF_ALPHA(audit_data)
66: Print("Krippendorff's α:", α)
67:
68: for each metric m ∈ {ASR, PLR, TU, trust_rounds} do
69:     test_ids, adj_p, δ, reject ← STATISTICAL_TESTS(R, attack_ids,
70:                         {(B1,B2), (B1,B3)}, m)
71:     aggregate by category and print summaries
72: end for
73:
74: // Communication overhead: compare median latency per trial
75: for each pair (B1,B2) and (B1,B3) do
76:     for each a ∈ A do
77:         med1 ← [median(trial['latencies']) for trial in R[(B1,a)]]
78:         med2 ← [median(trial['latencies']) for trial in R[(B2/B3,a)]]
79:         p, δ ← WILCOXON(med1, med2), CLIFF_DELTA(med2, med1)
80:         print p, δ
81:     end for
82: end for