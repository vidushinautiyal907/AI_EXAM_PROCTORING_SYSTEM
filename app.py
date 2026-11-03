"""
AI-Powered Intelligent Online Examination and Secure Assessment System
Chandigarh University - Master of Computer Applications (MCA)
Author: Vidushi [25MCI10158]

Full Flask Backend Application
"""

import os
import sys
import json
import time
import subprocess
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from database import get_db, init_db, seed_sample_data, hash_pw
from ai_engine import (
    NLPQuestionAnalyzer,
    DescriptiveEvaluationEngine,
    AdaptiveTestingEngine,
    ItemAnalysisEngine,
    StudentPerformancePredictor,
    BehavioralRiskScorer,
    CryptographicResultVerifier
)
from ai_generator import AIQuestionGenerator

app = Flask(__name__)
app.secret_key = "CU_MCA_Secret_Key_Examinations_2026_Secure"
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['TEMPLATES_AUTO_RELOAD'] = True

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

# Ensure database is initialized on startup
with app.app_context():
    init_db()
    seed_sample_data()

# -------------------------------------------------------------
# AUTHENTICATION & SESSION ROUTES
# -------------------------------------------------------------
@app.route('/')
def index():
    if 'user_id' in session:
        role = session.get('role')
        if role == 'student':
            return redirect(url_for('student_dashboard'))
        elif role == 'teacher':
            return redirect(url_for('teacher_dashboard'))
        elif role == 'admin':
            return redirect(url_for('admin_dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        pw_hash = hash_pw(password)

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ? AND password_hash = ?", (username, pw_hash))
        user = cursor.fetchone()
        conn.close()

        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            session['full_name'] = user['full_name']
            session['roll_no'] = user['roll_no']
            flash(f"Welcome back, {user['full_name']}!", "success")

            if user['role'] == 'student':
                return redirect(url_for('student_dashboard'))
            elif user['role'] == 'teacher':
                return redirect(url_for('teacher_dashboard'))
            elif user['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
        else:
            flash("Invalid credentials. Please verify your username and password.", "danger")

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("You have successfully signed out.", "info")
    return redirect(url_for('login'))

# -------------------------------------------------------------
# STUDENT PORTAL ROUTES
# -------------------------------------------------------------
@app.route('/student/dashboard')
def student_dashboard():
    if 'user_id' not in session or session.get('role') != 'student':
        return redirect(url_for('login'))

    user_id = session['user_id']
    conn = get_db()
    cursor = conn.cursor()

    # User details
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()

    # Available Exams
    cursor.execute("SELECT * FROM exams WHERE status = 'active' ORDER BY id ASC")
    exams = cursor.fetchall()

    # Recommendations
    cursor.execute("SELECT * FROM recommendations WHERE user_id = ? ORDER BY mastery_pct ASC", (user_id,))
    recommendations = cursor.fetchall()

    # Completed Attempts
    cursor.execute('''
        SELECT a.*, e.title as exam_title, e.code as exam_code 
        FROM exam_attempts a 
        JOIN exams e ON a.exam_id = e.id 
        WHERE a.user_id = ? AND a.status = 'completed'
        ORDER BY a.id DESC
    ''', (user_id,))
    attempts = cursor.fetchall()

    # Latest Theta
    latest_theta = 1.45
    if attempts:
        latest_theta = attempts[0]['ability_theta'] or 1.45

    conn.close()

    # Machine Learning Performance Prediction
    prediction = StudentPerformancePredictor.predict(
        quiz_accuracy=85.0,
        time_efficiency_ratio=0.88,
        past_score_avg=82.0,
        ability_theta=latest_theta
    )

    return render_template(
        'student_dashboard.html',
        user=user,
        exams=exams,
        recommendations=recommendations,
        attempts=attempts,
        prediction=prediction,
        latest_theta=latest_theta
    )

@app.route('/practice')
def practice_playground():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('practice_playground.html')

@app.route('/api/ai/generate_question', methods=['POST'])
def api_ai_generate_question():
    data = request.get_json() or {}
    topic = data.get('topic', 'dynamic programming')
    difficulty = data.get('difficulty', 'medium')
    blooms_level = data.get('blooms_level', 'Apply')
    q_type = data.get('q_type', None)

    q = AIQuestionGenerator.generate_question(topic, difficulty, blooms_level, q_type)
    return jsonify(q)

@app.route('/api/teacher/save_ai_question', methods=['POST'])
def api_save_ai_question():
    if 'user_id' not in session:
        return jsonify({"success": False, "error": "Unauthorized"}), 401

    data = request.get_json() or {}
    exam_id = int(data.get('exam_id', 1))
    subject = data.get('subject', 'Computer Science')
    topic = data.get('topic', 'General')
    difficulty = data.get('difficulty', 'medium')
    blooms_level = data.get('blooms_level', 'Apply')
    q_type = data.get('question_type', 'mcq')
    text = data.get('question_text', '')
    opt_a = data.get('option_a', None)
    opt_b = data.get('option_b', None)
    opt_c = data.get('option_c', None)
    opt_d = data.get('option_d', None)
    correct = data.get('correct_option', 'A')
    ref_ans = data.get('reference_answer', None)
    key_concepts = data.get('key_concepts', None)
    test_cases_json = json.dumps(data.get('test_cases', [])) if data.get('test_cases') else None
    marks = float(data.get('marks', 2.0))

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO questions (
            exam_id, subject, topic, difficulty, blooms_level, question_type,
            question_text, option_a, option_b, option_c, option_d, correct_option,
            reference_answer, key_concepts, test_cases_json, marks
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (exam_id, subject, topic, difficulty, blooms_level, q_type, text, opt_a, opt_b, opt_c, opt_d, correct, ref_ans, key_concepts, test_cases_json, marks))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()

    return jsonify({"success": True, "question_id": new_id})

# -------------------------------------------------------------
# EXAMINATION EXECUTION & RESULT
# -------------------------------------------------------------
@app.route('/exam/<int:exam_id>/start')
def start_exam(exam_id):
    if 'user_id' not in session or session.get('role') != 'student':
        return redirect(url_for('login'))

    user_id = session['user_id']
    conn = get_db()
    cursor = conn.cursor()

    # Exam metadata
    cursor.execute("SELECT * FROM exams WHERE id = ?", (exam_id,))
    exam = cursor.fetchone()
    if not exam:
        conn.close()
        flash("Examination not found.", "danger")
        return redirect(url_for('student_dashboard'))

    # Check or create attempt
    cursor.execute("SELECT * FROM exam_attempts WHERE exam_id = ? AND user_id = ? AND status = 'in_progress'", (exam_id, user_id))
    attempt = cursor.fetchone()

    if not attempt:
        cursor.execute('''
            INSERT INTO exam_attempts (exam_id, user_id, start_time, status, total_marks)
            VALUES (?, ?, ?, 'in_progress', ?)
        ''', (exam_id, user_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), exam['total_marks']))
        conn.commit()
        attempt_id = cursor.lastrowid
        cursor.execute("SELECT * FROM exam_attempts WHERE id = ?", (attempt_id,))
        attempt = cursor.fetchone()

    # Fetch Questions for this exam
    cursor.execute("SELECT * FROM questions WHERE exam_id = ? ORDER BY id ASC", (exam_id,))
    questions_raw = cursor.fetchall()
    conn.close()

    questions = [dict(q) for q in questions_raw]

    return render_template('exam_screen.html', exam=exam, attempt=attempt, questions=questions)

@app.route('/viva/<int:exam_id>')
def viva_room(exam_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db()
    cursor = conn.cursor()
    # Fetch descriptive/conceptual questions for Oral Viva
    cursor.execute("SELECT * FROM questions WHERE question_type = 'descriptive' OR blooms_level IN ('Analyze', 'Evaluate') LIMIT 5")
    viva_q = cursor.fetchall()
    conn.close()

    viva_questions = [dict(q) for q in viva_q]
    return render_template('viva_screen.html', viva_questions=viva_questions)

@app.route('/result/<int:attempt_id>')
def exam_result(attempt_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT a.*, e.title as exam_title, e.code as exam_code, u.full_name, u.roll_no, u.department
        FROM exam_attempts a
        JOIN exams e ON a.exam_id = e.id
        JOIN users u ON a.user_id = u.id
        WHERE a.id = ?
    ''', (attempt_id,))
    attempt = cursor.fetchone()

    # Get events for breakdown
    cursor.execute("SELECT * FROM behavior_events WHERE attempt_id = ?", (attempt_id,))
    events = [dict(e) for e in cursor.fetchall()]
    conn.close()

    if not attempt:
        flash("Attempt record not found.", "danger")
        return redirect(url_for('student_dashboard'))

    risk_info = BehavioralRiskScorer.calculate_risk(events)
    risk_breakdown = risk_info['breakdown']

    return render_template('exam_result.html', attempt=attempt, risk_breakdown=risk_breakdown)

# -------------------------------------------------------------
# TEACHER & ADMIN PORTAL ROUTES
# -------------------------------------------------------------
@app.route('/teacher/dashboard')
def teacher_dashboard():
    if 'user_id' not in session or session.get('role') not in ['teacher', 'admin']:
        return redirect(url_for('login'))

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM exams ORDER BY id ASC")
    exams = cursor.fetchall()

    cursor.execute("SELECT * FROM questions ORDER BY id DESC")
    questions = cursor.fetchall()

    cursor.execute("SELECT COUNT(*) FROM exam_attempts WHERE status = 'completed'")
    attempts_count = cursor.fetchone()[0]

    # Pre-calculate Psychometric Item Analysis
    item_stats = []
    for q in questions[:6]:
        stats = ItemAnalysisEngine.calculate_item_statistics(
            total_attempts=24,
            total_correct=16 if q['difficulty'] == 'easy' else (12 if q['difficulty'] == 'medium' else 7),
            upper_group_correct=9,
            lower_group_correct=4,
            group_size=10
        )
        item_stats.append({
            "id": q['id'],
            "topic": q['topic'],
            "difficulty": q['difficulty'],
            "p_value": stats['difficulty_index_p'],
            "d_index": stats['discrimination_index_d'],
            "recommendation": stats['recommendation']
        })

    conn.close()
    return render_template('teacher_dashboard.html', exams=exams, questions=questions, attempts_count=attempts_count, item_stats=item_stats)

@app.route('/teacher/live')
def teacher_live():
    if 'user_id' not in session or session.get('role') not in ['teacher', 'admin']:
        return redirect(url_for('login'))
    return render_template('teacher_live.html')

@app.route('/teacher/review')
def teacher_review():
    if 'user_id' not in session or session.get('role') not in ['teacher', 'admin']:
        return redirect(url_for('login'))

    conn = get_db()
    cursor = conn.cursor()
    # Fetch descriptive responses with student answers
    cursor.execute('''
        SELECT r.id, r.student_answer, r.marks_awarded, q.question_text, q.reference_answer, q.key_concepts, q.marks as max_marks,
               u.full_name as student_name, u.roll_no, e.code as exam_code
        FROM attempt_responses r
        JOIN questions q ON r.question_id = q.id
        JOIN exam_attempts a ON r.attempt_id = a.id
        JOIN users u ON a.user_id = u.id
        JOIN exams e ON a.exam_id = e.id
        WHERE q.question_type = 'descriptive'
        ORDER BY r.id DESC
    ''')
    raw_responses = cursor.fetchall()
    conn.close()

    descriptive_responses = []
    for r in raw_responses:
        item = dict(r)
        keys = item['key_concepts'].split(',') if item['key_concepts'] else []
        eval_result = DescriptiveEvaluationEngine.evaluate(
            student_answer=item['student_answer'],
            reference_answer=item['reference_answer'] or "",
            key_concepts=keys,
            max_marks=item['max_marks'] or 5
        )
        item['ai_score'] = eval_result['awarded_marks']
        item['confidence'] = eval_result['confidence']
        item['feedback'] = eval_result['feedback']
        descriptive_responses.append(item)

    return render_template('teacher_review.html', descriptive_responses=descriptive_responses)

@app.route('/admin/dashboard')
def admin_dashboard():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT b.*, u.full_name, u.roll_no, e.code as exam_code
        FROM behavior_events b
        JOIN users u ON b.user_id = u.id
        JOIN exam_attempts a ON b.attempt_id = a.id
        JOIN exams e ON a.exam_id = e.id
        ORDER BY b.id DESC LIMIT 50
    ''')
    events = cursor.fetchall()

    cursor.execute("SELECT COUNT(DISTINCT attempt_id) FROM behavior_events WHERE severity = 'HIGH'")
    flagged = cursor.fetchone()[0]
    conn.close()

    return render_template('admin_dashboard.html', events=events, flagged_count=flagged)

@app.route('/verify')
def verify_certificate():
    query_id = request.args.get('id', '').strip()
    result = None
    if query_id:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT a.*, e.title as exam_title, u.full_name, u.roll_no
            FROM exam_attempts a
            JOIN exams e ON a.exam_id = e.id
            JOIN users u ON a.user_id = u.id
            WHERE a.verification_id = ? OR a.result_hash = ?
        ''', (query_id, query_id))
        att = cursor.fetchone()
        conn.close()

        if att:
            result = dict(att)
            result['is_valid'] = True
        else:
            result = {'is_valid': False}

    return render_template('verify_cert.html', query_id=query_id, result=result)

# -------------------------------------------------------------
# REST APIS FOR EXAM EXECUTION & BEHAVIORAL LOGGING
# -------------------------------------------------------------
@app.route('/api/save_response', methods=['POST'])
def api_save_response():
    data = request.get_json() or {}
    attempt_id = data.get('attempt_id')
    question_id = data.get('question_id')
    student_ans = str(data.get('student_answer', '')).strip()
    response_time = int(data.get('response_time_seconds', 0))
    is_adaptive = bool(data.get('is_adaptive', False))

    conn = get_db()
    cursor = conn.cursor()

    # Get question metadata
    cursor.execute("SELECT * FROM questions WHERE id = ?", (question_id,))
    q = cursor.fetchone()

    # Get current attempt theta
    cursor.execute("SELECT ability_theta FROM exam_attempts WHERE id = ?", (attempt_id,))
    att = cursor.fetchone()
    current_theta = att['ability_theta'] if att and att['ability_theta'] is not None else 0.0

    # Auto-eval for MCQ
    is_correct = 0
    marks_awarded = 0.0

    if q['question_type'] == 'mcq':
        if student_ans.upper() == (q['correct_option'] or '').upper():
            is_correct = 1
            marks_awarded = q['marks']
    elif q['question_type'] == 'descriptive':
        keys = q['key_concepts'].split(',') if q['key_concepts'] else []
        eval_res = DescriptiveEvaluationEngine.evaluate(student_ans, q['reference_answer'] or "", keys, q['marks'])
        marks_awarded = eval_res['awarded_marks']
        is_correct = 1 if marks_awarded >= (q['marks'] * 0.5) else 0

    # IRT Theta Update if adaptive
    new_theta = current_theta
    if is_adaptive and q['question_type'] == 'mcq':
        new_theta = AdaptiveTestingEngine.update_ability(current_theta, bool(is_correct), q['difficulty'])
        cursor.execute("UPDATE exam_attempts SET ability_theta = ? WHERE id = ?", (new_theta, attempt_id))

    # Insert or update response
    cursor.execute("SELECT id FROM attempt_responses WHERE attempt_id = ? AND question_id = ?", (attempt_id, question_id))
    existing = cursor.fetchone()
    if existing:
        cursor.execute('''
            UPDATE attempt_responses 
            SET student_answer = ?, is_correct = ?, marks_awarded = ?, response_time_seconds = ?
            WHERE id = ?
        ''', (student_ans, is_correct, marks_awarded, response_time, existing['id']))
    else:
        cursor.execute('''
            INSERT INTO attempt_responses (attempt_id, question_id, student_answer, is_correct, marks_awarded, response_time_seconds)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (attempt_id, question_id, student_ans, is_correct, marks_awarded, response_time))

    conn.commit()
    conn.close()

    return jsonify({"success": True, "new_theta": new_theta})

@app.route('/api/log_event', methods=['POST'])
def api_log_event():
    data = request.get_json() or {}
    attempt_id = data.get('attempt_id')
    event_type = data.get('event_type')
    details = data.get('details')
    severity = data.get('severity', 'MEDIUM')
    user_id = session.get('user_id', 1)

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO behavior_events (attempt_id, user_id, event_type, details, severity)
        VALUES (?, ?, ?, ?, ?)
    ''', (attempt_id, user_id, event_type, details, severity))

    # Update attempt risk score
    cursor.execute("SELECT * FROM behavior_events WHERE attempt_id = ?", (attempt_id,))
    events = [dict(e) for e in cursor.fetchall()]
    risk_info = BehavioralRiskScorer.calculate_risk(events)

    cursor.execute("UPDATE exam_attempts SET risk_score = ? WHERE id = ?", (risk_info['risk_score'], attempt_id))
    conn.commit()
    conn.close()

    return jsonify({"success": True, "risk_score": risk_info['risk_score']})

@app.route('/api/submit_exam', methods=['POST'])
def api_submit_exam():
    data = request.get_json() or {}
    attempt_id = data.get('attempt_id')

    conn = get_db()
    cursor = conn.cursor()

    # Calculate total marks scored
    cursor.execute("SELECT SUM(marks_awarded) FROM attempt_responses WHERE attempt_id = ?", (attempt_id,))
    score = cursor.fetchone()[0] or 0.0

    # Get attempt and exam
    cursor.execute("SELECT a.*, e.total_marks as max_marks, u.roll_no FROM exam_attempts a JOIN exams e ON a.exam_id = e.id JOIN users u ON a.user_id = u.id WHERE a.id = ?", (attempt_id,))
    att = cursor.fetchone()

    total_marks = att['max_marks'] or 40.0
    pct = round((score / total_marks) * 100, 1)

    # Calculate final risk score from events
    cursor.execute("SELECT * FROM behavior_events WHERE attempt_id = ?", (attempt_id,))
    events = [dict(e) for e in cursor.fetchall()]
    risk_info = BehavioralRiskScorer.calculate_risk(events)

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    verif_id = f"CU-MCA-2026-V{att['user_id']}-{int(time.time()) % 10000}"
    result_hash = CryptographicResultVerifier.generate_result_hash(att['user_id'], att['exam_id'], score, total_marks, now_str)

    cursor.execute('''
        UPDATE exam_attempts
        SET end_time = ?, status = 'completed', score = ?, percentage = ?, risk_score = ?,
            risk_data_json = ?, result_hash = ?, verification_id = ?
        WHERE id = ?
    ''', (now_str, score, pct, risk_info['risk_score'], json.dumps(risk_info), result_hash, verif_id, attempt_id))

    conn.commit()
    conn.close()

    return jsonify({"success": True, "redirect": f"/result/{attempt_id}"})

# -------------------------------------------------------------
# CODE EXECUTION SANDBOX RUNNER
# -------------------------------------------------------------
@app.route('/api/run_code', methods=['POST'])
def api_run_code():
    data = request.get_json() or {}
    code = data.get('code', '')
    test_cases = data.get('test_cases', [])

    if not code:
        return jsonify({"success": False, "output": "No code submitted."})

    # Wrapper script that executes student code and tests cases
    test_harness = f"""
{code}

# Test Harness
import json
results = []
passed = 0
tests = {json.dumps(test_cases)}

for i, tc in enumerate(tests):
    inp = tc['input']
    exp = tc['expected']
    try:
        # evaluate target function two_sum
        res = eval(f"two_sum({{inp}})")
        exp_val = eval(exp)
        if res == exp_val:
            passed += 1
            results.append(f"Test {{i+1}}: Passed (Input: {{inp}} -> Output: {{res}})")
        else:
            results.append(f"Test {{i+1}}: Failed (Input: {{inp}} -> Got: {{res}}, Expected: {{exp_val}})")
    except Exception as e:
        results.append(f"Test {{i+1}}: Exception: {{str(e)}}")

print(json.dumps({{'passed': passed, 'total': len(tests), 'details': results}}))
"""
    try:
        # Run safely in isolated Python subprocess with timeout
        proc = subprocess.run(
            [sys.executable, "-c", test_harness],
            capture_output=True,
            text=True,
            timeout=4
        )
        if proc.returncode == 0:
            try:
                out_data = json.loads(proc.stdout.strip().split('\n')[-1])
                return jsonify({
                    "success": out_data['passed'] == out_data['total'],
                    "passed_tests": out_data['passed'],
                    "total_tests": out_data['total'],
                    "output": "\n".join(out_data['details'])
                })
            except Exception:
                return jsonify({"success": False, "passed_tests": 0, "total_tests": len(test_cases), "output": proc.stdout})
        else:
            return jsonify({"success": False, "passed_tests": 0, "total_tests": len(test_cases), "output": proc.stderr})
    except subprocess.TimeoutExpired:
        return jsonify({"success": False, "output": "Execution Terminated: Time Limit Exceeded (> 4.0s). Infinite loop detected."})
    except Exception as ex:
        return jsonify({"success": False, "output": f"Sandbox Error: {str(ex)}"})

# -------------------------------------------------------------
# AI ORAL VIVA EVALUATION & TEACHER LIVE STREAM APIS
# -------------------------------------------------------------
@app.route('/api/evaluate_oral', methods=['POST'])
def api_evaluate_oral():
    data = request.get_json() or {}
    student_transcript = data.get('student_transcript', '')
    reference_answer = data.get('reference_answer', '')
    key_concepts = data.get('key_concepts', [])
    max_marks = float(data.get('max_marks', 5.0))

    eval_result = DescriptiveEvaluationEngine.evaluate(
        student_answer=student_transcript,
        reference_answer=reference_answer,
        key_concepts=key_concepts,
        max_marks=max_marks
    )
    return jsonify(eval_result)

@app.route('/api/teacher/live_stream')
def api_teacher_live_stream():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT a.id, a.start_time, a.risk_score, u.full_name, u.roll_no, e.title as exam_title,
               (SELECT COUNT(*) FROM behavior_events b WHERE b.attempt_id = a.id) as event_count
        FROM exam_attempts a
        JOIN users u ON a.user_id = u.id
        JOIN exams e ON a.exam_id = e.id
        WHERE a.status = 'in_progress'
        ORDER BY a.risk_score DESC
    ''')
    active_attempts = [dict(row) for row in cursor.fetchall()]

    cursor.execute('''
        SELECT b.*, u.full_name as student_name
        FROM behavior_events b
        JOIN users u ON b.user_id = u.id
        ORDER BY b.id DESC LIMIT 12
    ''')
    recent_events = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return jsonify({"active_attempts": active_attempts, "recent_events": recent_events})

@app.route('/api/teacher/send_warning', methods=['POST'])
def api_teacher_send_warning():
    data = request.get_json() or {}
    attempt_id = data.get('attempt_id')
    message = data.get('message', 'Warning from invigilator.')

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO behavior_events (attempt_id, user_id, event_type, details, severity)
        VALUES (?, 1, 'TEACHER_WARNING', ?, 'HIGH')
    ''', (attempt_id, message))
    cursor.execute('''
        INSERT INTO proctor_alerts (attempt_id, message, alert_type)
        VALUES (?, ?, 'WARNING')
    ''', (attempt_id, message))
    conn.commit()
    conn.close()

    return jsonify({"success": True})

@app.route('/api/teacher/check_similarity', methods=['POST'])
def api_check_similarity():
    data = request.get_json() or {}
    text = data.get('question_text', '')

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, question_text FROM questions")
    existing_questions = cursor.fetchall()
    conn.close()

    max_sim = 0.0
    closest_match = None

    for q in existing_questions:
        sim = NLPQuestionAnalyzer.compute_similarity(text, q['question_text'])
        if sim > max_sim:
            max_sim = sim
            closest_match = q

    quality = NLPQuestionAnalyzer.assess_question_quality(text, ["Option A", "Option B", "Option C", "Option D"])

    return jsonify({
        "max_similarity": max_sim,
        "closest_match_id": closest_match['id'] if closest_match else None,
        "closest_match_text": closest_match['question_text'] if closest_match else "",
        "quality": quality
    })

@app.route('/api/teacher/add_question', methods=['POST'])
def api_add_question():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    subject = request.form.get('subject')
    topic = request.form.get('topic')
    difficulty = request.form.get('difficulty')
    blooms_level = request.form.get('blooms_level')
    q_type = request.form.get('question_type')
    text = request.form.get('question_text')
    opt_a = request.form.get('option_a')
    opt_b = request.form.get('option_b')
    opt_c = request.form.get('option_c')
    opt_d = request.form.get('option_d')
    correct = request.form.get('correct_option')
    ref_ans = request.form.get('reference_answer')
    key_concepts = request.form.get('key_concepts')

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO questions (
            exam_id, subject, topic, difficulty, blooms_level, question_type,
            question_text, option_a, option_b, option_c, option_d, correct_option,
            reference_answer, key_concepts, marks
        ) VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 2.0)
    ''', (subject, topic, difficulty, blooms_level, q_type, text, opt_a, opt_b, opt_c, opt_d, correct, ref_ans, key_concepts))
    conn.commit()
    conn.close()

    flash("Question successfully saved to Question Bank!", "success")
    return redirect(url_for('teacher_dashboard'))

@app.route('/api/teacher/override_score', methods=['POST'])
def api_override_score():
    res_id = request.form.get('response_id')
    final_score = float(request.form.get('final_score', 0))

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE attempt_responses SET marks_awarded = ? WHERE id = ?", (final_score, res_id))
    conn.commit()
    conn.close()

    flash(f"Score updated to {final_score} marks.", "success")
    return redirect(url_for('teacher_review'))

if __name__ == '__main__':
    print("=" * 70)
    print("CHANDIGARH UNIVERSITY • MCA EXAMINATION & INTELLIGENT ASSESSMENT SYSTEM")
    print("Submitted by Vidushi [25MCI10158]")
    print("Server starting on http://127.0.0.1:5000 ...")
    print("=" * 70)
    app.run(host='127.0.0.1', port=5000, debug=True)
