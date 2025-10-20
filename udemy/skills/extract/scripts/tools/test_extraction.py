#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Extraction Script

Tests the Udemy course extraction functionality with actual API endpoints
discovered during research phase.

Usage:
    python test_extraction.py
"""

import sys
import os
from pathlib import Path

# Add parent directory (scripts/) to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from auth import Authenticator
from api_client import UdemyAPIClient
from file_writer import CourseFileWriter


def test_authentication():
    """Test Phase 1: Authentication"""
    print("=" * 60)
    print("TEST PHASE 1: Authentication")
    print("=" * 60)

    # Use current working directory as base (works for both local and Git-installed plugins)
    project_root = Path.cwd() / 'udemy-research'

    try:
        print("\n1. Loading credentials from .env...")
        auth = Authenticator(project_root)
        print("  ✓ Credentials loaded")

        print("\n2. Checking for session cookies...")
        if auth.has_session_cookies():
            cookies = auth.get_session_cookies()
            print(f"  ✓ {len(cookies)} cookies loaded from cookies.json")
            print(f"    Cookie names: {', '.join(cookies.keys())}")
        else:
            print("  ⚠️  No cookies.json found")
            print("    Note: You may need to create cookies.json with session cookies")
            print("    See IMPLEMENTATION_PHASE_GUIDE.md for instructions")

        print("\n3. Generating auth headers...")
        headers = auth.get_auth_headers()
        print("  ✓ Headers generated")
        print(f"    Headers: {', '.join(headers.keys())}")

        print("\n✓ Phase 1: Authentication PASSED")
        return auth, project_root

    except Exception as e:
        print(f"\n✗ Phase 1: Authentication FAILED")
        print(f"  Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def test_api_client(auth, project_root):
    """Test Phase 2: API Client Initialization"""
    print("\n" + "=" * 60)
    print("TEST PHASE 2: API Client Initialization")
    print("=" * 60)

    try:
        print("\n1. Initializing API client...")
        # Use risesmart.udemy.com as base URL (from research)
        base_url = "https://risesmart.udemy.com"
        auth_headers = auth.get_auth_headers()

        client = UdemyAPIClient(
            base_url=base_url,
            auth_headers=auth_headers,
            project_root=project_root
        )
        print("  ✓ API client initialized")

        print("\n2. Checking API documentation loading...")
        print(f"  Documented endpoints: {len(client.documented_endpoints)}")
        if client.documented_endpoints:
            for name, endpoint in client.documented_endpoints.items():
                print(f"    - {name}: {endpoint}")

        print("\n✓ Phase 2: API Client Initialization PASSED")
        return client

    except Exception as e:
        print(f"\n✗ Phase 2: API Client Initialization FAILED")
        print(f"  Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def test_course_structure(client):
    """Test Phase 3: Course Structure Extraction"""
    print("\n" + "=" * 60)
    print("TEST PHASE 3: Course Structure Extraction")
    print("=" * 60)

    try:
        # Use "The Ultimate React Course 2025" course ID from research
        # Course ID: 4471614
        course_id = "4471614"

        print(f"\n1. Fetching course structure for course ID: {course_id}...")
        print("   (This is 'The Ultimate React Course 2025' used in research)")

        course_data = client.get_course_structure(course_id)

        if not course_data:
            print("\n  ✗ Failed to fetch course structure")
            print("  This likely means:")
            print("    - Session cookies are missing or expired")
            print("    - You don't have access to this course")
            print("    - API endpoint has changed")
            return None

        print("\n2. Parsing course data...")
        course_title = course_data.get('title', 'Unknown')
        sections = course_data.get('sections', [])
        total_lectures = sum(len(s.get('lectures', [])) for s in sections)

        print(f"  ✓ Course: {course_title}")
        print(f"  ✓ Sections: {len(sections)}")
        print(f"  ✓ Total lectures: {total_lectures}")

        if sections:
            print("\n3. Sample section structure:")
            first_section = sections[0]
            print(f"  Section: {first_section.get('title', 'Untitled')}")
            print(f"  Lectures in section: {len(first_section.get('lectures', []))}")

            if first_section.get('lectures'):
                first_lecture = first_section['lectures'][0]
                print(f"\n  Sample lecture:")
                print(f"    ID: {first_lecture.get('id')}")
                print(f"    Title: {first_lecture.get('title', 'Untitled')}")
                print(f"    Has asset: {'asset' in first_lecture}")

        print("\n✓ Phase 3: Course Structure Extraction PASSED")
        return course_data

    except Exception as e:
        print(f"\n✗ Phase 3: Course Structure Extraction FAILED")
        print(f"  Error: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_transcript_download(client, course_data):
    """Test Phase 4: Single Transcript Download"""
    print("\n" + "=" * 60)
    print("TEST PHASE 4: Single Transcript Download")
    print("=" * 60)

    if not course_data:
        print("\n  ⚠️  Skipping (no course data from Phase 3)")
        return False

    try:
        # Get first lecture with a transcript
        course_id = "4471614"
        sections = course_data.get('sections', [])

        print("\n1. Finding first lecture with content...")

        test_lecture = None
        for section in sections:
            for lecture in section.get('lectures', []):
                lecture_id = lecture.get('id')
                if lecture_id:
                    test_lecture = lecture
                    break
            if test_lecture:
                break

        if not test_lecture:
            print("  ✗ No lectures found in course structure")
            return False

        lecture_id = test_lecture.get('id')
        lecture_title = test_lecture.get('title', 'Untitled')

        print(f"  Testing with lecture: {lecture_title}")
        print(f"  Lecture ID: {lecture_id}")

        print("\n2. Fetching transcript...")
        transcript = client.get_lecture_transcript(
            course_id=course_id,
            lecture_id=lecture_id
        )

        if not transcript:
            print("  ⚠️  No transcript available for this lecture")
            print("  Note: Not all lectures have transcripts")
            print("\nTrying next lecture...")

            # Try a few more lectures
            for section in sections:
                for lecture in section.get('lectures', []):
                    lecture_id = lecture.get('id')
                    lecture_title = lecture.get('title', 'Untitled')
                    if lecture_id:
                        print(f"\n  Trying: {lecture_title} (ID: {lecture_id})")
                        transcript = client.get_lecture_transcript(
                            course_id=course_id,
                            lecture_id=lecture_id
                        )
                        if transcript:
                            break
                if transcript:
                    break

        if not transcript:
            print("\n  ⚠️  Could not find any lectures with transcripts")
            print("  This might mean:")
            print("    - Course doesn't have transcripts enabled")
            print("    - VTT URLs are not accessible")
            print("    - Session cookies expired")
            return False

        print("\n3. Analyzing transcript...")
        print(f"  ✓ Transcript segments: {len(transcript)}")

        # Show first few segments
        print("\n  Sample transcript content:")
        for i, cue in enumerate(transcript[:3], 1):
            time = cue.get('time', '00:00')
            text = cue.get('text', '')
            preview = text[:60] + ('...' if len(text) > 60 else '')
            print(f"    [{time}] {preview}")

        print("\n✓ Phase 4: Single Transcript Download PASSED")
        return True

    except Exception as e:
        print(f"\n✗ Phase 4: Single Transcript Download FAILED")
        print(f"  Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all test phases"""
    print("\n" + "=" * 60)
    print("UDEMY EXTRACTION TEST SUITE")
    print("=" * 60)
    print("\nThis test will verify:")
    print("  1. Authentication with session cookies")
    print("  2. API client initialization")
    print("  3. Course structure extraction")
    print("  4. Transcript download functionality")
    print("\n" + "=" * 60)

    # Phase 1: Authentication
    auth, project_root = test_authentication()

    # Phase 2: API Client
    client = test_api_client(auth, project_root)

    # Phase 3: Course Structure
    course_data = test_course_structure(client)

    # Phase 4: Transcript Download
    transcript_success = test_transcript_download(client, course_data)

    # Final Summary
    print("\n" + "=" * 60)
    print("TEST SUITE SUMMARY")
    print("=" * 60)
    print("✓ Phase 1: Authentication - PASSED")
    print("✓ Phase 2: API Client - PASSED")
    print(f"{'✓' if course_data else '✗'} Phase 3: Course Structure - {'PASSED' if course_data else 'FAILED'}")
    print(f"{'✓' if transcript_success else '⚠️ '} Phase 4: Transcript Download - {'PASSED' if transcript_success else 'PARTIAL/FAILED'}")
    print("=" * 60)

    if course_data and transcript_success:
        print("\n✓ ALL TESTS PASSED!")
        print("\nYou can now run the full extraction:")
        print('  python extract.py "https://risesmart.udemy.com/course/react-the-complete-guide-incl-redux/"')
    elif course_data:
        print("\n⚠️  PARTIAL SUCCESS")
        print("  Course structure works, but transcripts may not be available")
        print("  Check that:")
        print("    - The course has transcripts enabled")
        print("    - Your session cookies are valid")
    else:
        print("\n✗ TESTS FAILED")
        print("\nTroubleshooting:")
        print("  1. Make sure cookies.json exists with valid session cookies")
        print("  2. Verify you have access to the test course (ID: 4471614)")
        print("  3. Check that cookies haven't expired (they expire after a few hours)")
        print("\nTo get cookies.json:")
        print("  1. Login to risesmart.udemy.com in your browser")
        print("  2. Open DevTools (F12) > Application > Cookies")
        print("  3. Copy access_token and client_id cookies")
        print('  4. Create cookies.json: {"access_token": "...", "client_id": "..."}')

    print()


if __name__ == '__main__':
    main()
