import streamlit as st
import sqlite3
import os
import tempfile
import face_recognition
import numpy as np
from PIL import Image

st.set_page_config(page_title="AI Voter Verification", page_icon="🗳️")
st.title("🗳️ AI Voter Verification System")
st.markdown("---")

def get_voter(voter_id):
    conn = sqlite3.connect("voters.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, voter_id, name, photo_path, has_voted FROM voters WHERE voter_id = ?",
        (voter_id,)
    )
    row = cursor.fetchone()
    conn.close()
    return row

def mark_as_voted(voter_id):
    conn = sqlite3.connect("voters.db")
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE voters SET has_voted = 1 WHERE voter_id = ?",
        (voter_id,)
    )
    conn.commit()
    conn.close()

def compare_faces(registered_photo_path, live_photo_bytes):
    try:
        registered_image = face_recognition.load_image_file(registered_photo_path)
        registered_encodings = face_recognition.face_encodings(registered_image)
        if len(registered_encodings) == 0:
            st.error("No face found in registered photo!")
            return False, 0.0
        registered_encoding = registered_encodings[0]
        live_image = Image.open(live_photo_bytes).convert("RGB")
        live_array = np.array(live_image)
        live_encodings = face_recognition.face_encodings(live_array)
        if len(live_encodings) == 0:
            st.error("No face found in live photo - please try again!")
            return False, 0.0
        live_encoding = live_encodings[0]
        distance = face_recognition.face_distance([registered_encoding], live_encoding)[0]
        confidence = round((1 - distance) * 100, 1)
        is_match = distance < 0.6
        return is_match, confidence
    except Exception as e:
        st.error(f"Error: {e}")
        return False, 0.0

st.subheader("Step 1 — Enter Voter ID")
voter_id_input = st.text_input("Voter ID", placeholder="e.g. VOT001")

if voter_id_input:
    voter = get_voter(voter_id_input.strip().upper())
    if voter is None:
        st.error("❌ Voter ID not found!")
    else:
        db_id, v_id, name, photo_path, has_voted = voter
        st.success(f"✅ Found: {name}")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Registered photo**")
            if os.path.exists(photo_path):
                st.image(photo_path, width=200)
            else:
                st.warning("Photo file not found!")
        if has_voted == 1:
            st.error("🚫 FRAUD ALERT: This voter already voted!")
            st.stop()
        st.markdown("---")
        st.subheader("Step 2 — Take Live Photo")
        test_mode = st.checkbox("Use photo upload instead of camera")
        if test_mode:
            live_photo = st.file_uploader("Upload a face photo", type=["jpg","jpeg","png"])
        else:
            live_photo = st.camera_input("Take your photo now")
        if live_photo is not None:
            with col2:
                st.markdown("**Your live photo**")
                st.image(live_photo, width=200)
            st.markdown("---")
            st.subheader("Step 3 — AI Verification Result")
            with st.spinner("AI is comparing faces... please wait"):
                is_match, confidence = compare_faces(photo_path, live_photo)
            if is_match:
                st.success(f"✅ Face Verified! Confidence: {confidence}%")
                st.balloons()
                mark_as_voted(v_id)
                st.success("✅ Vote recorded! Thank you.")
            else:
                st.error(f"❌ Face does NOT match! Confidence: {confidence}%")
                st.warning("⚠️ Possible fraud attempt detected!")
