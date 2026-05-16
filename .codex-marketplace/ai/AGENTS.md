# ai — Codex AGENTS

> **Bootstrap:** Load `using-arkhe-skills` first — it maps Claude-only tools (`AskUserQuestion`, `TaskCreate`, `EnterPlanMode`, `Skill`, `Agent`) to Codex equivalents.

AI engineering toolkit for production-ready LLM applications

## Skills

- **lyra** — Transform vague inputs into precision-optimized AI prompts for Claude, ChatGPT, Gemini, or other LLMs. Use when user mentions "optimize prompt", "improve prompt", "lyra", "prompt engineering", or nee…

## Commands as Trigger Phrases

### When the user says "/ai:improve-agent"

Systematic agent improvement through performance analysis and prompt engineering. Use when user wants to optimize an agent, improve agent accuracy, reduce hallucinations, tune prompts, or mentions "a…

# Agent Performance Optimization Workflow

Systematic improvement of existing agents through performance analysis, prompt engineering, and continuous iteration.

[Extended thinking: Agent optimization requires a data-driven approach combining performance metrics, user feedback analysis, and advanced prompt engineering techniques. Success depends on systematic evaluation, targeted improvements, and rigorous testing with rollback capabilities for production safety.]

## Phase 1: Performance Analysis and Baseline Metrics

Comprehensive analysis of agent performance using context-manager for historical data collection.

### 1.1 Gather Performance Data
```
Use: context-manager
Command: analyze-agent-performance $ARGUMENTS --days 30
```

Collect metrics including:
- Task completion rate (successful vs failed tasks)
- Response accuracy and factual correctness
- Tool usage efficiency (correct tools, call frequency)
- Average response time and token consumption
- User satisfaction indicators (corrections, retries)
- Hallucination incidents and error patterns

### 1.2 User Feedback Pattern Analysis

Identify recurring patterns in user interactions:
- **Correction patterns**: Where users consistently modify outputs
- **Clarification requests**: Common areas of ambiguity
- **Task abandonment**: Points where users give up
- **Follow-up questions**: Indicators of incomplete responses
- **Positive feedback**: Successful patterns to preserve

### 1.3 Failure Mode Classification

Categorize failures by root cause:
- **Instruction misunderstanding**: Role or task confusion
- **Output format errors**: Structure or formatting issues
- **Context loss**: Long conversation degradation
- **Tool misuse**: Incorrect or inefficient tool selection
- **Constraint violations**: Safety or business rule breaches
- **Edge case handling**: Unusual input scenarios

### 1.4 Baseline Performance Report

Generate quantitative baseline metrics:
```
Performance Baseline:
- Task Success Rate: [X%]
- Average Corrections per Task: [Y]
- Tool Call Efficiency: [Z%]
- User Satisfaction Score: [1-10]
- Average Response Latency: [Xms]
- Token Efficiency Ratio: [X:Y]
```

## Phase 2: Prompt Engineering Improvements

Apply advanced prompt optimization techniques using prompt-engineer agent.

### 2.1 Chain-of-Thought Enhancement

Implement structured reasoning patterns:
```
Use: prompt-engineer
Technique: chain-of-thought-optimization
```

- Add explicit reasoning steps: "Let's approach this step-by-step..."
- Include self-verification checkpoints: "Before proceeding, verify that..."
- Implement recursive decomposition for complex tasks
- Add reasoning trace visibility for debugging

### 2.2 Few-Shot Example Optimization

Curate high-quality examples from successful interactions:
- **Select diverse examples** covering common use cases
- **Include edge cases** that previously failed
- **Show both positive and negative examples** with explanations
- **Order examples** from simple to complex
- **Annotate examples** with key decision points

Example structure:
```
Good Example:
Input: [User request]
Reasoning: [Step-by-step thought process]
Output: [Successful response]
Why this works: [Key success factors]

Bad Example:
Input: [Similar request]
Output: [Failed response]
Why this fails: [Specific issues]
Correct approach: [Fixed version]
```

### 2.3 Role Definition Refinement

Strengthen agent identity and capabilities:
- **Core purpose**: Clear, single-sentence mission
- **Expertise domains**: Specific knowledge areas
- **Behavioral traits**: Personality and interaction style
- **Tool proficiency**: Available tools and when to use them
- **Constraints**: What the agent should NOT do
- **Success criteria**: How to measure task completion

### 2.4 Constitutional AI Integration

Implement self-correction mechanisms:
```
Constitutional Principles:
1. Verify factual accuracy before responding
2. Self-check for potential biases or harmful content
3. Validate output format matches requirements
4. Ensure response completeness
5. Maintain consistency with previous responses
```

Add critique-and-revise loops:
- Initial response generation
- Self-critique against principles
- Automatic revision if issues detected
- Final validation before output

### 2.5 Output Format Tuning

Optimize response structure:
- **Structured templates** for common tasks
- **Dynamic formatting** based on complexity
- **Progressive disclosure** for detailed information
- **Markdown optimization** for readability
- **Code block formatting** with syntax highlighting
- **Table and list generation** for data presentation

## Phase 3: Testing and Validation

Comprehensive testing framework with A/B comparison.

### 3.1 Test Suite Development

Create representative test scenarios:
```
Test Categories:
1. Golden path scenarios (common successful cases)
2. Previously failed tasks (regression testing)
3. Edge cases and corner scenarios
4. Stress tests (complex, multi-step tasks)
5. Adversarial inputs (potential breaking points)
6. Cross-domain tasks (combining capabilities)
```

### 3.2 A/B Testing Framework

Compare original vs improved agent:
```
Use: parallel-test-runner
Config:
  - Agent A: Original version
  - Agent B: Improved version
  - Test set: 100 representative tasks
  - Metrics: Success rate, speed, token usage
  - Evaluation: Blind human review + automated scoring
```

Statistical significance testing:
- Minimum sample size: 100 tasks per variant
- Confidence level: 95% (p < 0.05)
- Effect size calculation (Cohen's d)
- Power analysis for future tests

### 3.3 Evaluation Metrics

Comprehensive scoring framework:

**Task-Level Metrics:**
- Completion rate (binary success/failure)
- Correctness score (0-100% accuracy)
- Efficiency score (steps taken vs optimal)
- Tool usage appropriateness
- Response relevance and completeness

**Quality Metrics:**
- Hallucination rate (factual errors per response)
- Consistency score (alignment with previous responses)
- Format compliance (matches specified structure)
- Safety score (constraint adherence)
- User satisfaction prediction

**Performance Metrics:**
- Response latency (time to first token)
- Total generation time
- Token consumption (input + output)
- Cost per task (API usage fees)
- Memory/context efficiency

### 3.4 Human Evaluation Protocol

Structured human review process:
- Blind evaluation (evaluators don't know version)
- Standardized rubric with clear criteria
- Multiple evaluators per sample (inter-rater reliability)
- Qualitative feedback collection
- Preference ranking (A vs B comparison)

## Phase 4: Version Control and Deployment

Safe rollout with monitoring and rollback capabilities.

### 4.1 Version Management

Systematic versioning strategy:
```
Version Format: agent-name-v[MAJOR].[MINOR].[PATCH]
Example: customer-support-v2.3.1

MAJOR: Significant capability changes
MINOR: Prompt improvements, new examples
PATCH: Bug fixes, minor adjustments
```

Maintain version history:
- Git-based prompt storage
- Changelog with improvement details
- Performance metrics per version
- Rollback procedures documented

### 4.2 Staged Rollout

Progressive deployment strategy:
1. **Alpha testing**: Internal team validation (5% traffic)
2. **Beta testing**: Selected users (20% traffic)
3. **Canary release**: Gradual increase (20% → 50% → 100%)
4. **Full deployment**: After success criteria met
5. **Monitoring period**: 7-day observation window

### 4.3 Rollback Procedures

Quick recovery mechanism:
```
Rollback Triggers:
- Success rate drops >10% from baseline
- Critical errors increase >5%
- User complaints spike
- Cost per task increases >20%
- Safety violations detected

Rollback Process:
1. Detect issue via monitoring
2. Alert team immediately
3. Switch to previous stable version
4. Analyze root cause
5. Fix and re-test before retry
```

### 4.4 Continuous Monitoring

Real-time performance tracking:
- Dashboard with key metrics
- Anomaly detection alerts
- User feedback collection
- Automated regression testing
- Weekly performance reports

## Success Criteria

Agent improvement is successful when:
- Task success rate improves by ≥15%
- User corrections decrease by ≥25%
- No increase in safety violations
- Response time remains within 10% of baseline
- Cost per task doesn't increase >5%
- Positive user feedback increases

## Post-Deployment Review

After 30 days of production use:
1. Analyze accumulated performance data
2. Compare against baseline and targets
3. Identify new improvement opportunities
4. Document lessons learned
5. Plan next optimization cycle

## Continuous Improvement Cycle

Establish regular improvement cadence:
- **Weekly**: Monitor metrics and collect feedback
- **Monthly**: Analyze patterns and plan improvements
- **Quarterly**: Major version updates with new capabilities
- **Annually**: Strategic review and architecture updates

Remember: Agent optimization is an iterative process. Each cycle builds upon previous learnings, gradually improving performance while maintaining stability and safety.

### When the user says "/ai:multi-agent-optimize"

AI-powered multi-agent coordination for system performance optimization. Use when user wants to optimize multi-agent workflows, reduce latency across agents, improve agent coordination, or mentions "…

# Multi-Agent Optimization Toolkit

## Role: AI-Powered Multi-Agent Performance Engineering Specialist

### Context
The Multi-Agent Optimization Tool is an advanced AI-driven framework designed to holistically improve system performance through intelligent, coordinated agent-based optimization. Leveraging cutting-edge AI orchestration techniques, this tool provides a comprehensive approach to performance engineering across multiple domains.

### Core Capabilities
- Intelligent multi-agent coordination
- Performance profiling and bottleneck identification
- Adaptive optimization strategies
- Cross-domain performance optimization
- Cost and efficiency tracking

## Arguments Handling
The tool processes optimization arguments with flexible input parameters:
- `$TARGET`: Primary system/application to optimize
- `$PERFORMANCE_GOALS`: Specific performance metrics and objectives
- `$OPTIMIZATION_SCOPE`: Depth of optimization (quick-win, comprehensive)
- `$BUDGET_CONSTRAINTS`: Cost and resource limitations
- `$QUALITY_METRICS`: Performance quality thresholds

## 1. Multi-Agent Performance Profiling

### Profiling Strategy
- Distributed performance monitoring across system layers
- Real-time metrics collection and analysis
- Continuous performance signature tracking

#### Profiling Agents
1. **Database Performance Agent**
   - Query execution time analysis
   - Index utilization tracking
   - Resource consumption monitoring

2. **Application Performance Agent**
   - CPU and memory profiling
   - Algorithmic complexity assessment
   - Concurrency and async operation analysis

3. **Frontend Performance Agent**
   - Rendering performance metrics
   - Network request optimization
   - Core Web Vitals monitoring

### Profiling Code Example
```python
def multi_agent_profiler(target_system):
    agents = [
        DatabasePerformanceAgent(target_system),
        ApplicationPerformanceAgent(target_system),
        FrontendPerformanceAgent(target_system)
    ]

    performance_profile = {}
    for agent in agents:
        performance_profile[agent.__class__.__name__] = agent.profile()

    return aggregate_performance_metrics(performance_profile)
```

## 2. Context Window Optimization

### Optimization Techniques
- Intelligent context compression
- Semantic relevance filtering
- Dynamic context window resizing
- Token budget management

### Context Compression Algorithm
```python
def compress_context(context, max_tokens=4000):
    # Semantic compression using embedding-based truncation
    compressed_context = semantic_truncate(
        context,
        max_tokens=max_tokens,
        importance_threshold=0.7
    )
    return compressed_context
```

## 3. Agent Coordination Efficiency

### Coordination Principles
- Parallel execution design
- Minimal inter-agent communication overhead
- Dynamic workload distribution
- Fault-tolerant agent interactions

### Orchestration Framework
```python
class MultiAgentOrchestrator:
    def __init__(self, agents):
        self.agents = agents
        self.execution_queue = PriorityQueue()
        self.performance_tracker = PerformanceTracker()

    def optimize(self, target_system):
        # Parallel agent execution with coordinated optimization
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = {
                executor.submit(agent.optimize, target_system): agent
                for agent in self.agents
            }

            for future in concurrent.futures.as_completed(futures):
                agent = futures[future]
                result = future.result()
                self.performance_tracker.log(agent, result)
```

## 4. Parallel Execution Optimization

### Key Strategies
- Asynchronous agent processing
- Workload partitioning
- Dynamic resource allocation
- Minimal blocking operations

## 5. Cost Optimization Strategies

### LLM Cost Management
- Token usage tracking
- Adaptive model selection
- Caching and result reuse
- Efficient prompt engineering

### Cost Tracking Example
```python
class CostOptimizer:
    def __init__(self):
        self.token_budget = 100000  # Monthly budget
        self.token_usage = 0
        self.model_costs = {
            'gpt-4': 0.03,
            'claude-3-sonnet': 0.015,
            'claude-3-haiku': 0.0025
        }

    def select_optimal_model(self, complexity):
        # Dynamic model selection based on task complexity and budget
        pass
```

## 6. Latency Reduction Techniques

### Performance Acceleration
- Predictive caching
- Pre-warming agent contexts
- Intelligent result memoization
- Reduced round-trip communication

## 7. Quality vs Speed Tradeoffs

### Optimization Spectrum
- Performance thresholds
- Acceptable degradation margins
- Quality-aware optimization
- Intelligent compromise selection

## 8. Monitoring and Continuous Improvement

### Observability Framework
- Real-time performance dashboards
- Automated optimization feedback loops
- Machine learning-driven improvement
- Adaptive optimization strategies

## Reference Workflows

### Workflow 1: E-Commerce Platform Optimization
1. Initial performance profiling
2. Agent-based optimization
3. Cost and performance tracking
4. Continuous improvement cycle

### Workflow 2: Enterprise API Performance Enhancement
1. Comprehensive system analysis
2. Multi-layered agent optimization
3. Iterative performance refinement
4. Cost-efficient scaling strategy

## Key Considerations
- Always measure before and after optimization
- Maintain system stability during optimization
- Balance performance gains with resource consumption
- Implement gradual, reversible changes

Target Optimization: $ARGUMENTS
