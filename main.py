import numpy as np
from scipy import stats
from statsmodels.stats.multitest import multipletests
import krippendorff

# ============================================================================
# 1. TESTBED DEFINITION (as per LaTeX)
# ============================================================================
FRAMEWORKS = ['AutoGen', 'CrewAI', 'LangGraph']
MODELS = ['Claude Opus 4.7', 'GPT-class', 'Llama-class']

# 10 agents: distribute across frameworks and models (simplified mapping)
AGENTS = []
agent_id = 0
# We need 10 agents; arbitrary distribution
for f in FRAMEWORKS:
    for m in MODELS:
        if len(AGENTS) < 10:
            AGENTS.append({'id': f'agent_{agent_id}', 'framework': f, 'model': m})
            agent_id += 1
        else:
            break
# If not enough, fill remaining with duplicates (should be exactly 10)
while len(AGENTS) < 10:
    AGENTS.append({'id': f'agent_{agent_id}', 'framework': FRAMEWORKS[agent_id % 3], 'model': MODELS[agent_id % 3]})
    agent_id += 1

# MCP servers (tool categories)
MCP_SERVERS = [
    'code_execution_sandbox',
    'web_search_retrieval',
    'personal_data_hipaa',
    'email_service',
    'sandboxed_payments'
]

# ============================================================================
# 2. ATTACK CORPUS (A1--A8, 50+ variants each → ~450 attacks)
# ============================================================================
ATTACK_CATEGORIES = {
    'A1': 'Direct Prompt Injection',
    'A2': 'Indirect Prompt Injection',
    'A3': 'Inter-Agent Prompt Infection',
    'A4': 'Tool Poisoning',
    'A5': 'Capability Over-Claiming',
    'A6': 'Byzantine Agent',
    'A7': 'Sybil and Collusion Attacks',
    'A8': 'Data Exfiltration (Trifecta)'
}

def generate_attack_corpus(variants_per_category=50):
    """
    Creates ~450 attack instances (8 categories × variants_per_category).
    For demonstration, default variants_per_category is 50; reduce to 2 for quick tests.
    """
    attacks = []
    for cat_id, cat_name in ATTACK_CATEGORIES.items():
        for v in range(variants_per_category):
            attack = {
                'attack_id': f'{cat_id}_{v+1}',
                'category': cat_id,
                'description': f'{cat_name} variant {v+1}',
                'target_agent': np.random.choice(AGENTS)['id'],  # which agent is attacked
                'prompt': f'Malicious instruction for {cat_name} variant {v+1}',
                'tools_involved': np.random.choice(MCP_SERVERS, size=np.random.randint(1,3), replace=False).tolist()
            }
            attacks.append(attack)
    return attacks

# ============================================================================
# 3. BASELINES (B1, B2, B3)
# ============================================================================
BASELINES = ['B1_unhardened', 'B2_best_practice', 'B3_ARGUS']

# ============================================================================
# 4. METRICS SIMULATION (dummy data generation)
# ============================================================================
def simulate_trial_metrics(config, attack, rng):
    """
    Simulates one trial under the given configuration and attack.
    Returns a dictionary with all required metrics.
    """
    # ---- ASR (attack success rate) ----
    # For dummy, B1 has high ASR, B2 lower, B3 even lower.
    base_asr = {'B1_unhardened': 0.8, 'B2_best_practice': 0.4, 'B3_ARGUS': 0.2}
    asr = rng.binomial(1, base_asr[config])

    # ---- PLR (privacy leakage rate) ----
    base_plr = {'B1_unhardened': 0.6, 'B2_best_practice': 0.3, 'B3_ARGUS': 0.15}
    plr = rng.binomial(1, base_plr[config])

    # ---- TU (task utility for benign tasks) ----
    # Assume all configs maintain high utility (0.95 success) with slight degradation in B3
    base_tu = {'B1_unhardened': 0.95, 'B2_best_practice': 0.95, 'B3_ARGUS': 0.90}
    tu = rng.binomial(1, base_tu[config])

    # ---- Communication Overhead (list of per-message latencies in ms) ----
    # Simulate a random number of inter-agent messages (5-15) and generate latencies.
    n_messages = rng.integers(5, 16)
    # Latency distribution depends on config: B1 (fast), B2 (overhead from filtering), B3 (overhead from provenance)
    mu_map = {'B1_unhardened': 10, 'B2_best_practice': 18, 'B3_ARGUS': 25}
    sigma = 3.0
    latencies = rng.normal(mu_map[config], sigma, n_messages).clip(min=1).tolist()

    # ---- Trust Convergence Time (rounds) ----
    # Simulate the number of rounds for trust score to fall below threshold.
    # B1: trust never converges (high value), B2: moderate, B3: quick convergence.
    mu_rounds = {'B1_unhardened': 20, 'B2_best_practice': 10, 'B3_ARGUS': 5}
    # Use geometric distribution: number of trials until first success with p.
    p = 1.0 / mu_rounds[config]
    trust_rounds = rng.geometric(p)

    # ---- Auditability Score (simulate 3 human raters 1-5) ----
    # True auditability: B1 poor, B2 moderate, B3 excellent.
    true_audit = {'B1_unhardened': 1.5, 'B2_best_practice': 3.0, 'B3_ARGUS': 4.5}
    base = np.clip(np.round(true_audit[config]), 1, 5)
    ratings = np.clip(np.round(base + rng.normal(0, 0.6, 3)), 1, 5).astype(int).tolist()

    return {
        'ASR': asr,
        'PLR': plr,
        'TU': tu,
        'latencies': latencies,
        'trust_rounds': trust_rounds,
        'auditability_ratings': ratings   # 3 rater scores
    }

# ============================================================================
# 5. EXPERIMENT RUNNER
# ============================================================================
def run_experiment(configurations, attacks, trials=30):
    """
    Runs `trials` independent trials for each (config, attack) pair.
    Returns:
        trial_results: dict keyed by (config, attack_id) containing list of dicts with all metrics.
        all_auditability_ratings: list of [rater1, rater2, rater3] for all trials.
    """
    trial_results = {}
    all_auditability_ratings = []

    for config in configurations:
        for attack in attacks:
            attack_id = attack['attack_id']
            trial_scores = []
            for t in range(trials):
                # Randomised seeds per protocol
                seed = np.random.randint(0, 1_000_000)
                rng = np.random.default_rng(seed)

                # --- TESTBED INITIALISATION (placeholder) ---
                # TODO: Set up isolated network, start agents, MCP servers with
                # tools from attack['tools_involved'], using the seed.

                # --- LLM SAMPLING & ATTACK EXECUTION (placeholder) ---
                # TODO: Inject attack['prompt'] into target_agent, run the scenario.

                # Collect metrics for this trial
                metrics = simulate_trial_metrics(config, attack, rng)
                trial_scores.append(metrics)

                # Store auditability ratings for Krippendorff's alpha
                all_auditability_ratings.append(metrics['auditability_ratings'])

            trial_results[(config, attack_id)] = trial_scores
            print(f"Completed {trials} trials: Config={config}, Attack={attack_id}")
    return trial_results, all_auditability_ratings

# ============================================================================
# 6. STATISTICAL ANALYSIS
# ============================================================================
def calculate_cliffs_delta(x, y):
    n_x, n_y = len(x), len(y)
    mat = np.zeros((n_x, n_y))
    for i in range(n_x):
        for j in range(n_y):
            if x[i] > y[j]: mat[i, j] = 1
            elif x[i] < y[j]: mat[i, j] = -1
    return np.sum(mat) / (n_x * n_y)

def perform_wilcoxon_tests(trial_results, attack_ids, config_pairs, metric_key):
    """
    For a given metric (e.g., 'ASR'), performs paired Wilcoxon signed-rank
    tests for each attack and each config pair, then applies Holm-Bonferroni
    correction across all tests.
    Returns arrays of adjusted p-values, effect sizes, and rejection flags.
    """
    all_p_values = []
    all_effect_sizes = []
    test_identifiers = []  # (attack_id, pair) for tracking

    for attack_id in attack_ids:
        for (cfgA, cfgB) in config_pairs:
            scoresA = [trial[metric_key] for trial in trial_results[(cfgA, attack_id)]]
            scoresB = [trial[metric_key] for trial in trial_results[(cfgB, attack_id)]]
            # Wilcoxon signed-rank test (two-tailed)
            stat, p = stats.wilcoxon(scoresA, scoresB)
            delta = calculate_cliffs_delta(scoresB, scoresA)  # positive = B improves over A
            all_p_values.append(p)
            all_effect_sizes.append(delta)
            test_identifiers.append((attack_id, cfgA, cfgB))

    # Holm-Bonferroni correction across all tests for this metric
    reject, pvals_corrected, _, _ = multipletests(all_p_values, alpha=0.05, method='holm')
    return test_identifiers, pvals_corrected, all_effect_sizes, reject

def summarize_by_category(test_ids, adj_p, effect_sizes, rejections, attack_category_map):
    """
    Aggregates results per attack category: median adjusted p-value,
    proportion significant, median effect size.
    """
    from collections import defaultdict
    cat_data = defaultdict(list)
    for (attack_id, cfgA, cfgB), p, eff, rej in zip(test_ids, adj_p, effect_sizes, rejections):
        cat = attack_category_map[attack_id]
        cat_data[cat].append({'p': p, 'eff': eff, 'sig': rej})
    summary = {}
    for cat in sorted(cat_data.keys()):
        vals = cat_data[cat]
        median_p = np.median([v['p'] for v in vals])
        prop_sig = np.mean([v['sig'] for v in vals])
        median_eff = np.median([v['eff'] for v in vals])
        summary[cat] = (median_p, prop_sig, median_eff)
    return summary

# ============================================================================
# 7. MAIN
# ============================================================================
if __name__ == "__main__":
    # For demonstration, generate a small attack corpus (2 variants per category → 16 attacks).
    # Increase to 50 to match the full corpus (450 attacks).
    print("Generating attack corpus...")
    attacks = generate_attack_corpus(variants_per_category=2)  # change to 50 for full experiment
    attack_ids = [a['attack_id'] for a in attacks]
    attack_category_map = {a['attack_id']: a['category'] for a in attacks}

    # Configurations: all three baselines
    configs = BASELINES

    # Run the 30-trial experiment
    print(f"\nRunning {len(configs)} configurations × {len(attacks)} attacks × 30 trials...")
    trial_results, all_audit_ratings = run_experiment(configs, attacks, trials=30)

    # ---- Inter‑rater reliability: Krippendorff's α on auditability scores ----
    audit_array = np.array(all_audit_ratings).T   # shape (3, N_items)
    alpha = krippendorff.alpha(reliability_data=audit_array, level_of_measurement='ordinal')
    print(f"\nKrippendorff's alpha (auditability, all trials): {alpha:.4f}")

    # ---- Statistical comparisons: B1 vs B2 and B1 vs B3 for each metric ----
    config_pairs = [('B1_unhardened', 'B2_best_practice'),
                    ('B1_unhardened', 'B3_ARGUS')]

    # Metrics to test (excluding latencies, which are list-valued; we'll test median latency)
    scalar_metrics = {
        'ASR': 'Attack Success Rate',
        'PLR': 'Privacy Leakage Rate',
        'TU': 'Task Utility',
        'trust_rounds': 'Trust Convergence Time (rounds)'
    }

    for metric_key, metric_name in scalar_metrics.items():
        print(f"\n--- Metric: {metric_name} ---")
        test_ids, adj_p, eff, rej = perform_wilcoxon_tests(trial_results, attack_ids, config_pairs, metric_key)
        summary = summarize_by_category(test_ids, adj_p, eff, rej, attack_category_map)
        for cat in sorted(summary.keys()):
            med_p, prop_sig, med_eff = summary[cat]
            print(f"  Category {cat}: median adj. p = {med_p:.4f}, "
                  f"significant fraction = {prop_sig:.2f}, median Cliff's δ = {med_eff:.3f}")
        # Also report global summary
        global_med_p = np.median(adj_p)
        global_sig = np.mean(rej)
        global_med_eff = np.median(eff)
        print(f"  Global across all attacks: median adj. p = {global_med_p:.4f}, "
              f"significant proportion = {global_sig:.2f}, median Cliff's δ = {global_med_eff:.3f}")

    # ---- Communication Overhead: compare median latency per trial ----
    print("\n--- Metric: Communication Overhead (median latency per trial) ---")
    # For each trial, compute the median of the latencies list
    for cfgA, cfgB in config_pairs:
        print(f"  Comparing {cfgA} vs {cfgB}:")
        for attack_id in attack_ids:
            median_lats_A = [np.median(t['latencies']) for t in trial_results[(cfgA, attack_id)]]
            median_lats_B = [np.median(t['latencies']) for t in trial_results[(cfgB, attack_id)]]
            stat, p = stats.wilcoxon(median_lats_A, median_lats_B)
            delta = calculate_cliffs_delta(median_lats_B, median_lats_A)
            print(f"    Attack {attack_id}: p = {p:.4f}, Cliff's δ = {delta:.3f}")
        # Could also apply Holm correction across attacks; omitted for brevity
