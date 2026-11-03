"""
Database Management & Initial Seeder for Intelligent Online Examination System
SQLite based - zero configuration required for VS Code!
"""

import sqlite3
import os
import json
import hashlib
from datetime import datetime

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'exam_system.db')

def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def hash_pw(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    # Users Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL, -- 'student', 'teacher', 'admin'
        full_name TEXT NOT NULL,
        roll_no TEXT,
        department TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Exams Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS exams (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        subject TEXT NOT NULL,
        code TEXT UNIQUE NOT NULL,
        duration_minutes INTEGER NOT NULL,
        is_adaptive INTEGER DEFAULT 0, -- 1 for IRT adaptive
        blueprint_json TEXT,
        pass_percentage REAL DEFAULT 40.0,
        total_marks REAL DEFAULT 50.0,
        status TEXT DEFAULT 'active', -- 'draft', 'active', 'completed'
        created_by INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Questions Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        exam_id INTEGER,
        subject TEXT NOT NULL,
        topic TEXT NOT NULL,
        difficulty TEXT NOT NULL, -- 'easy', 'medium', 'hard'
        blooms_level TEXT NOT NULL, -- 'Remember', 'Understand', 'Apply', 'Analyze', 'Evaluate'
        question_type TEXT NOT NULL, -- 'mcq', 'descriptive', 'code'
        question_text TEXT NOT NULL,
        option_a TEXT,
        option_b TEXT,
        option_c TEXT,
        option_d TEXT,
        correct_option TEXT, -- 'A', 'B', 'C', 'D'
        reference_answer TEXT,
        key_concepts TEXT, -- Comma-separated or JSON
        test_cases_json TEXT, -- For coding questions [{"input": "...", "expected": "..."}]
        marks REAL DEFAULT 2.0,
        expected_time_seconds INTEGER DEFAULT 60,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (exam_id) REFERENCES exams (id)
    )
    ''')

    # Exam Attempts Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS exam_attempts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        exam_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        end_time TIMESTAMP,
        status TEXT DEFAULT 'in_progress', -- 'in_progress', 'completed', 'terminated'
        score REAL DEFAULT 0.0,
        total_marks REAL DEFAULT 0.0,
        percentage REAL DEFAULT 0.0,
        ability_theta REAL DEFAULT 0.0,
        risk_score INTEGER DEFAULT 0,
        risk_data_json TEXT,
        result_hash TEXT,
        verification_id TEXT,
        FOREIGN KEY (exam_id) REFERENCES exams (id),
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')

    # Responses Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS attempt_responses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        attempt_id INTEGER NOT NULL,
        question_id INTEGER NOT NULL,
        student_answer TEXT,
        is_correct INTEGER DEFAULT 0,
        marks_awarded REAL DEFAULT 0.0,
        response_time_seconds INTEGER DEFAULT 0,
        ai_feedback_json TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (attempt_id) REFERENCES exam_attempts (id),
        FOREIGN KEY (question_id) REFERENCES questions (id)
    )
    ''')

    # Camera-Free Behavioral Events Log Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS behavior_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        attempt_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        event_type TEXT NOT NULL, -- 'TAB_SWITCH', 'FULLSCREEN_EXIT', 'COPY_PASTE', 'AUDIO_ANOMALY', 'KEYSTROKE_BURST', 'RAPID_SUBMIT'
        details TEXT,
        severity TEXT DEFAULT 'MEDIUM', -- 'LOW', 'MEDIUM', 'HIGH'
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (attempt_id) REFERENCES exam_attempts (id),
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')

    # Learning Recommendations Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS recommendations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        topic TEXT NOT NULL,
        mastery_pct REAL NOT NULL,
        status TEXT NOT NULL, -- 'Needs Revision', 'Mastered', 'Moderate'
        suggested_action TEXT,
        resource_link TEXT,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')

    # Live Proctoring Notifications (For Teacher Command Center)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS proctor_alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        attempt_id INTEGER NOT NULL,
        message TEXT NOT NULL,
        alert_type TEXT DEFAULT 'WARNING',
        acknowledged INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    conn.commit()
    conn.close()

def seed_sample_data():
    conn = get_db()
    cursor = conn.cursor()

    # Check if already seeded
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] > 0:
        conn.close()
        return

    print("Seeding initial database with users, MCA exams, question banks, and demo attempts...")

    # 1. Insert Users
    users_data = [
        ('vidushi', hash_pw('password123'), 'student', 'Vidushi', '25MCI10158', 'Master of Computer Applications (MCA)'),
        ('rahul', hash_pw('password123'), 'student', 'Rahul Sharma', '25MCI10159', 'Master of Computer Applications (MCA)'),
        ('teacher', hash_pw('password123'), 'teacher', 'Prof. Dr. A. K. Verma', 'FAC-CS-108', 'Computer Science & Engineering'),
        ('admin', hash_pw('admin123'), 'admin', 'Exam Controller Office', 'ADMIN-CU-01', 'Academic Assessment Directorate')
    ]
    cursor.executemany(
        "INSERT INTO users (username, password_hash, role, full_name, roll_no, department) VALUES (?, ?, ?, ?, ?, ?)",
        users_data
    )

    # 2. Insert Exams
    exams_data = [
        (
            'Advanced Data Structures & Algorithms (MCA-201)',
            'Computer Science',
            'EXAM-MCA-201',
            30,
            1, # is_adaptive
            json.dumps({"topic_distribution": {"Dynamic Programming": 30, "Trees & Graphs": 40, "Sorting & Complexity": 30}, "difficulty_mix": {"easy": 30, "medium": 40, "hard": 30}}),
            40.0,
            40.0,
            'active',
            3
        ),
        (
            'Machine Learning & Artificial Intelligence (MCA-305)',
            'Artificial Intelligence',
            'EXAM-MCA-305',
            25,
            1,
            json.dumps({"topic_distribution": {"Supervised Learning": 40, "Neural Networks": 40, "Optimization": 20}}),
            40.0,
            35.0,
            'active',
            3
        ),
        (
            'Software Engineering & Cloud Computing (MCA-104)',
            'Software Engineering',
            'EXAM-MCA-104',
            20,
            0, # Standard fixed exam
            json.dumps({"topic_distribution": {"SDLC": 50, "Agile & Microservices": 50}}),
            40.0,
            30.0,
            'active',
            3
        )
    ]
    cursor.executemany(
        "INSERT INTO exams (title, subject, code, duration_minutes, is_adaptive, blueprint_json, pass_percentage, total_marks, status, created_by) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        exams_data
    )

    # 3. Insert Questions (MCQs, Coding, Descriptive with Bloom's Taxonomy & IRT metadata)
    # Exam 1: MCA-201 (DS & Algo)
    questions_mca201 = [
        # Easy
        (
            1, 'Computer Science', 'Sorting & Complexity', 'easy', 'Remember', 'mcq',
            'What is the worst-case time complexity of standard QuickSort algorithm?',
            'O(n log n)', 'O(n^2)', 'O(log n)', 'O(n)',
            'B', None, None, None, 2.0, 45
        ),
        (
            1, 'Computer Science', 'Trees & Graphs', 'easy', 'Understand', 'mcq',
            'Which traversal method of a Binary Search Tree (BST) yields elements in sorted ascending order?',
            'Pre-order traversal', 'Post-order traversal', 'In-order traversal', 'Level-order traversal',
            'C', None, None, None, 2.0, 45
        ),
        (
            1, 'Computer Science', 'Trees & Graphs', 'easy', 'Remember', 'mcq',
            'In a full binary tree with N internal nodes, how many leaf nodes are present?',
            'N', 'N - 1', 'N + 1', '2N',
            'C', None, None, None, 2.0, 45
        ),
        # Medium
        (
            1, 'Computer Science', 'Dynamic Programming', 'medium', 'Apply', 'mcq',
            'Which optimal substructure property distinguishes Dynamic Programming from Greedy algorithms?',
            'Overlapping subproblems with optimal sub-solutions', 'Greedy choice at every local step', 'Depth-first search pruning', 'Divide and conquer without caching',
            'A', None, None, None, 3.0, 60
        ),
        (
            1, 'Computer Science', 'Trees & Graphs', 'medium', 'Analyze', 'mcq',
            'In Dijkstra\'s shortest path algorithm with a Min-Heap priority queue, what is the tight asymptotic time complexity?',
            'O(V^2)', 'O((V + E) log V)', 'O(E log E + V)', 'O(V * E)',
            'B', None, None, None, 3.0, 75
        ),
        (
            1, 'Computer Science', 'Dynamic Programming', 'medium', 'Apply', 'mcq',
            'What is the space complexity of solving the 0/1 Knapsack problem when optimized with a 1D DP array of capacity W?',
            'O(N * W)', 'O(W)', 'O(N)', 'O(2^N)',
            'B', None, None, None, 3.0, 60
        ),
        # Hard
        (
            1, 'Computer Science', 'Trees & Graphs', 'hard', 'Evaluate', 'mcq',
            'In an AVL Tree, after deleting a node, what is the maximum number of rotations required to rebalance the entire tree in the worst case?',
            'At most 1 single rotation', 'At most 2 double rotations', 'O(log n) rotations', 'No rotations needed',
            'C', None, None, None, 4.0, 90
        ),
        (
            1, 'Computer Science', 'Sorting & Complexity', 'hard', 'Evaluate', 'mcq',
            'What is the theoretical lower bound comparison time complexity for any comparison-based sorting algorithm in the decision-tree model?',
            'Omega(n)', 'Omega(n log n)', 'Omega(n^1.5)', 'Omega(log n!) which simplifies to Omega(n log n)',
            'D', None, None, None, 4.0, 90
        ),
        # Descriptive Question
        (
            1, 'Computer Science', 'Dynamic Programming', 'medium', 'Analyze', 'descriptive',
            'Explain the principle of memoization vs tabulation in dynamic programming with an example of Fibonacci sequence or Longest Common Subsequence.',
            None, None, None, None, None,
            'Memoization is a top-down caching approach that stores subproblem results upon recursion. Tabulation is an iterative bottom-up approach constructing the table from base cases up. Both eliminate recomputations of overlapping subproblems, reducing exponential time to polynomial O(N).',
            'memoization,tabulation,top-down,bottom-up,overlapping subproblems,cache,complexity',
            None, 5.0, 180
        ),
        # Coding Sandbox Question
        (
            1, 'Computer Science', 'Sorting & Complexity', 'medium', 'Apply', 'code',
            'Write a Python function `two_sum(nums, target)` that returns the indices of the two numbers in list `nums` such that they add up to `target`. Assume exactly one solution exists.',
            None, None, None, None, None,
            'def two_sum(nums, target):\n    lookup = {}\n    for i, num in enumerate(nums):\n        diff = target - num\n        if diff in lookup:\n            return [lookup[diff], i]\n        lookup[num] = i\n    return []',
            'hashmap,dictionary,lookup,linear time,O(n)',
            json.dumps([
                {"input": "[2, 7, 11, 15], 9", "expected": "[0, 1]"},
                {"input": "[3, 2, 4], 6", "expected": "[1, 2]"},
                {"input": "[3, 3], 6", "expected": "[0, 1]"}
            ]),
            6.0, 240
        )
    ]

    # Exam 2: MCA-305 (Machine Learning)
    questions_mca305 = [
        (
            2, 'Artificial Intelligence', 'Supervised Learning', 'easy', 'Remember', 'mcq',
            'Which metric is best suited to evaluate classification on a severely imbalanced dataset?',
            'Accuracy', 'F1-Score / Area Under PR Curve', 'Mean Squared Error (MSE)', 'R-Squared',
            'B', None, None, None, 2.0, 45
        ),
        (
            2, 'Artificial Intelligence', 'Neural Networks', 'medium', 'Understand', 'mcq',
            'Why does the vanishing gradient problem primarily occur with Sigmoid activation in deep networks?',
            'The derivative of sigmoid is bounded between 0 and 0.25, shrinking gradients during backpropagation',
            'Sigmoid causes weights to diverge to infinity',
            'Sigmoid is discontinuous at zero',
            'Sigmoid computes negative loss',
            'A', None, None, None, 3.0, 60
        ),
        (
            2, 'Artificial Intelligence', 'Optimization', 'hard', 'Analyze', 'mcq',
            'How does the Adam optimizer compute adaptive learning rates for each parameter?',
            'It combines both first moment (momentum) and second raw moment (uncentered variance) with bias correction',
            'It keeps the learning rate strictly constant throughout epochs',
            'It randomly scales learning rates via stochastic sampling',
            'It calculates second-order Hessian matrix inversions',
            'A', None, None, None, 4.0, 75
        ),
        (
            2, 'Artificial Intelligence', 'Supervised Learning', 'medium', 'Analyze', 'descriptive',
            'Differentiate between Bias and Variance in machine learning models and describe how regularization techniques mitigate overfitting.',
            None, None, None, None, None,
            'High bias leads to underfitting because the model is too simplistic to capture underlying patterns. High variance causes overfitting because the model memorizes training noise and fails to generalize. Regularization techniques like L1 Lasso and L2 Ridge penalize large model weights, constraining model complexity and balancing the bias-variance tradeoff.',
            'bias,variance,underfitting,overfitting,generalization,regularization,L1,L2,tradeoff',
            None, 5.0, 180
        )
    ]

    for q in questions_mca201 + questions_mca305:
        cursor.execute('''
        INSERT INTO questions (
            exam_id, subject, topic, difficulty, blooms_level, question_type,
            question_text, option_a, option_b, option_c, option_d,
            correct_option, reference_answer, key_concepts, test_cases_json,
            marks, expected_time_seconds
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', q)

    # 4. Insert a completed past sample attempt for Vidushi so analytics look live and rich!
    cursor.execute('''
    INSERT INTO exam_attempts (
        exam_id, user_id, start_time, end_time, status, score, total_marks, percentage, ability_theta, risk_score, risk_data_json, result_hash, verification_id
    ) VALUES (
        1, 1, '2026-10-25 10:00:00', '2026-10-25 10:24:15', 'completed', 34.0, 40.0, 85.0, 1.45, 12,
        '{"tab_switches": 0, "fullscreen_exits": 0, "copy_pastes": 0, "audio_violations": 0, "classification": "CLEAN / LOW RISK"}',
        'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
        'CU-MCA-2026-V10158-9482'
    )
    ''')

    # Recommendations for Vidushi
    recommendations_data = [
        (1, 'Dynamic Programming', 68.0, 'Moderate', 'Review 2D Memoization patterns and solve Knapsack & LCS variations.', 'https://geeksforgeeks.org/dynamic-programming/'),
        (1, 'Trees & Graphs', 92.0, 'Mastered', 'Excellent mastery. Practice Advanced Disjoint Set Union (DSU) and Segment Trees.', 'https://cp-algorithms.com/data_structures/segment_tree.html'),
        (1, 'Sorting & Complexity', 88.0, 'Mastered', 'Solid understanding of Master Theorem and amortized analysis.', 'https://en.wikipedia.org/wiki/Master_theorem_(analysis_of_algorithms)')
    ]
    cursor.executemany(
        "INSERT INTO recommendations (user_id, topic, mastery_pct, status, suggested_action, resource_link) VALUES (?, ?, ?, ?, ?, ?)",
        recommendations_data
    )

    conn.commit()
    conn.close()
    print("Database initialization and initial seeding complete!")

if __name__ == '__main__':
    init_db()
    seed_sample_data()
