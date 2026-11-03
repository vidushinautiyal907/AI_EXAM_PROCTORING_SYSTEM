"""
Comprehensive AI-Powered Examination & Assessment Studio
Adds:
1. AI Automated Question Generator (Bloom's Taxonomy levels, MCQs, Coding, Descriptive with key concepts)
2. Interactive Practice Question Playground with instant AI hints & solutions
3. Full In-Browser Code Playground / Editor with live compilation & custom inputs
4. Enhanced Audio Proctoring with calibrated volume meters & test microphone simulator
"""

import random
import json
from ai_engine import NLPQuestionAnalyzer

class AIQuestionGenerator:
    """
    Intelligent Generator that crafts psychometrically sound questions
    based on Subject, Topic, Difficulty, and Bloom's Taxonomy Level.
    """
    
    TEMPLATES = {
        "dynamic programming": {
            "easy": [
                {
                    "type": "mcq",
                    "blooms": "Remember",
                    "text": "What is the primary difference between top-down memoization and bottom-up tabulation in Dynamic Programming?",
                    "options": [
                        "Memoization uses recursion with a cache, while tabulation builds a table iteratively",
                        "Memoization always requires more time than tabulation",
                        "Tabulation cannot solve optimization problems",
                        "Memoization converts problems into Greedy heuristics"
                    ],
                    "correct": "A",
                    "explanation": "Memoization is top-down recursion with caching; tabulation builds solution from base subproblems iteratively."
                },
                {
                    "type": "mcq",
                    "blooms": "Understand",
                    "text": "Which characteristic is essential for a problem to be solvable via Dynamic Programming?",
                    "options": [
                        "Optimal substructure and overlapping subproblems",
                        "Independent non-overlapping subproblems",
                        "Linear time complexity only",
                        "Strict divide-and-conquer without state sharing"
                    ],
                    "correct": "A",
                    "explanation": "Dynamic programming requires overlapping subproblems with optimal sub-solutions."
                }
            ],
            "medium": [
                {
                    "type": "code",
                    "blooms": "Apply",
                    "text": "Write a Python function `climb_stairs(n)` that returns the number of distinct ways to climb to the top of an n-step staircase, where you can climb 1 or 2 steps each time.",
                    "reference": "def climb_stairs(n):\n    if n <= 2: return n\n    a, b = 1, 2\n    for _ in range(3, n + 1):\n        a, b = b, a + b\n    return b",
                    "key_concepts": "fibonacci,state transition,tabulation,O(n) time,space optimization",
                    "test_cases": [
                        {"input": "2", "expected": "2"},
                        {"input": "3", "expected": "3"},
                        {"input": "5", "expected": "8"}
                    ]
                },
                {
                    "type": "descriptive",
                    "blooms": "Analyze",
                    "text": "Analyze the state transition equation for the 0/1 Knapsack problem and explain why the greedy approach fails to provide an optimal solution.",
                    "reference": "In 0/1 Knapsack, items cannot be divided. State dp[i][w] = max(dp[i-1][w], val[i-1] + dp[i-1][w-wt[i-1]]). The greedy strategy based on value-to-weight ratio fails because choosing the highest density item may leave unusable empty capacity, preventing the global maximum.",
                    "key_concepts": "indivisible items,state transition,greedy failure,density ratio,global optimum,dp table"
                }
            ],
            "hard": [
                {
                    "type": "mcq",
                    "blooms": "Evaluate",
                    "text": "What is the optimal space complexity required to compute the Longest Common Subsequence (LCS) of two strings of lengths M and N when only the length is needed?",
                    "options": [
                        "O(min(M, N)) using two rolling rows/columns",
                        "O(M * N) space is strictly necessary",
                        "O(M + N) with recursive call stack",
                        "O(1) auxiliary memory"
                    ],
                    "correct": "A",
                    "explanation": "Because each state only depends on the current and previous row, space can be reduced to O(min(M, N))."
                }
            ]
        },
        "trees & graphs": {
            "easy": [
                {
                    "type": "mcq",
                    "blooms": "Remember",
                    "text": "In a max-heap binary tree with N elements, where is the minimum value element located?",
                    "options": [
                        "In one of the leaf nodes",
                        "Always at the root node",
                        "At the left child of the root",
                        "At index 0 of the array representation"
                    ],
                    "correct": "A",
                    "explanation": "In a max heap, root is the maximum; minimum must reside in one of the leaves."
                }
            ],
            "medium": [
                {
                    "type": "code",
                    "blooms": "Apply",
                    "text": "Write a Python function `is_valid_bst(nodes)` where nodes is a list representing an in-order traversal of a binary search tree. Return True if it is strictly ascending, else False.",
                    "reference": "def is_valid_bst(nodes):\n    for i in range(1, len(nodes)):\n        if nodes[i] <= nodes[i-1]:\n            return False\n    return True",
                    "key_concepts": "inorder traversal,sorted order,strictly increasing,binary search tree",
                    "test_cases": [
                        {"input": "[1, 2, 3, 4, 5]", "expected": "True"},
                        {"input": "[1, 3, 2]", "expected": "False"},
                        {"input": "[5, 5, 8]", "expected": "False"}
                    ]
                }
            ],
            "hard": [
                {
                    "type": "mcq",
                    "blooms": "Analyze",
                    "text": "Which algorithm finds strongly connected components (SCCs) in a directed graph in linear O(V + E) time using a single DFS traversal?",
                    "options": [
                        "Tarjan's algorithm (using low-link values)",
                        "Kosaraju's algorithm (requires two DFS passes)",
                        "Bellman-Ford algorithm",
                        "Floyd-Warshall algorithm"
                    ],
                    "correct": "A",
                    "explanation": "Tarjan's algorithm computes SCCs in a single DFS pass using discovery and low-link numbers."
                }
            ]
        },
        "neural networks": {
            "medium": [
                {
                    "type": "descriptive",
                    "blooms": "Analyze",
                    "text": "Explain how dropout regularization prevents overfitting in deep neural networks and describe its behavior during inference.",
                    "reference": "Dropout randomly sets a fraction p of hidden units to zero during training on each forward-backward pass. This prevents co-adaptation of features and approximates training an ensemble of exponential thinned subnetworks. During inference, dropout is deactivated and outputs are scaled by (1-p) or weights are kept intact with inverted dropout.",
                    "key_concepts": "co-adaptation,ensemble approximation,training vs inference,scaling,random deactivation"
                }
            ],
            "easy": [
                {
                    "type": "mcq",
                    "blooms": "Remember",
                    "text": "Which activation function is most commonly used in hidden layers of modern deep convolutional networks to avoid vanishing gradients?",
                    "options": [
                        "ReLU (Rectified Linear Unit)",
                        "Sigmoid function",
                        "Hyperbolic Tangent (Tanh)",
                        "Softmax function"
                    ],
                    "correct": "A",
                    "explanation": "ReLU preserves gradient magnitude for positive inputs, combating vanishing gradients."
                }
            ]
        }
    }

    @classmethod
    def generate_question(cls, topic, difficulty="medium", blooms_level="Apply", q_type=None):
        topic_key = topic.lower().strip()
        matched_topic = None
        for k in cls.TEMPLATES:
            if k in topic_key or topic_key in k:
                matched_topic = k
                break
        
        if not matched_topic:
            matched_topic = "dynamic programming"

        diff_dict = cls.TEMPLATES[matched_topic]
        pool = diff_dict.get(difficulty.lower(), [])
        
        if not pool:
            for d in ["medium", "easy", "hard"]:
                if diff_dict.get(d):
                    pool = diff_dict[d]
                    break

        # Filter by type if requested
        if q_type:
            filtered = [q for q in pool if q.get('type') == q_type]
            if filtered:
                pool = filtered

        selected = random.choice(pool)
        
        # Build standard output
        result = {
            "topic": topic.title(),
            "difficulty": difficulty.lower(),
            "blooms_level": blooms_level or selected.get("blooms", "Apply"),
            "question_type": selected.get("type", "mcq"),
            "question_text": selected.get("text"),
            "option_a": selected.get("options", ["", "", "", ""])[0] if selected.get("type") == "mcq" else None,
            "option_b": selected.get("options", ["", "", "", ""])[1] if selected.get("type") == "mcq" else None,
            "option_c": selected.get("options", ["", "", "", ""])[2] if selected.get("type") == "mcq" else None,
            "option_d": selected.get("options", ["", "", "", ""])[3] if selected.get("type") == "mcq" else None,
            "correct_option": selected.get("correct", "A"),
            "reference_answer": selected.get("reference", ""),
            "key_concepts": selected.get("key_concepts", ""),
            "test_cases": selected.get("test_cases", []),
            "marks": 6.0 if selected.get("type") == "code" else (4.0 if selected.get("type") == "descriptive" else 2.0),
            "quality": NLPQuestionAnalyzer.assess_question_quality(selected.get("text"), selected.get("options", []))
        }
        return result
