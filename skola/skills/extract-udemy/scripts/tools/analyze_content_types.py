#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.8"
# dependencies = []
# ///
"""
Content Type Analysis Tool

Analyzes a Udemy course to identify all content types present,
including those not currently being extracted.

This helps document what resources, quizzes, and other content
types could be implemented in future versions.
"""

import sys
import json
from pathlib import Path
from collections import defaultdict

# Add parent directory (scripts/) to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from auth import Authenticator
from api_client import UdemyAPIClient


def analyze_course_content(course_url, output_file=None):
    """
    Analyze all content types in a course.

    Args:
        course_url: Full Udemy course URL
        output_file: Optional path to save analysis report
    """
    # Use current working directory as base (works for both local and Git-installed plugins)
    project_root = Path.cwd() / 'udemy-research'

    print("=" * 60)
    print("Content Type Analysis Tool")
    print("=" * 60)
    print(f"Course URL: {course_url}\n")

    # Initialize authentication
    print("🔐 Authenticating...")
    auth = Authenticator(project_root)
    headers = auth.get_auth_headers()
    print("  ✓ Authenticated\n")

    # Initialize API client
    api_client = UdemyAPIClient(
        base_url=course_url.split('/course/')[0],
        auth_headers=headers,
        project_root=project_root
    )

    # Extract course slug and get structure
    course_slug = course_url.rstrip('/').split('/')[-1]
    print(f"📚 Fetching course structure for: {course_slug}")
    course_data = api_client.get_course_structure(course_slug)

    if not course_data:
        print("✗ Failed to fetch course structure")
        return

    print(f"  ✓ Found {len(course_data['sections'])} sections\n")

    # Analysis statistics
    stats = {
        'content_types': defaultdict(int),
        'asset_types': defaultdict(int),
        'has_transcripts': 0,
        'has_supplementary_assets': 0,
        'has_quiz_data': 0,
        'has_coding_exercise': 0,
        'has_downloadable_resources': 0,
        'promotional_content': 0,
        'total_lectures': 0
    }

    # Detailed findings
    findings = {
        'lectures_with_resources': [],
        'lectures_with_quizzes': [],
        'lectures_with_coding_exercises': [],
        'asset_type_examples': defaultdict(list),
        'content_type_examples': defaultdict(list)
    }

    print("🔍 Analyzing lecture content types...\n")

    lecture_num = 1
    for section_idx, section in enumerate(course_data['sections'], 1):
        section_title = section.get('title', f'Section {section_idx}')
        lectures = section.get('lectures', [])

        print(f"Section {section_idx}: {section_title} ({len(lectures)} lectures)")

        for lecture in lectures:
            stats['total_lectures'] += 1
            lecture_title = lecture.get('title', f'Lecture {lecture_num}')

            # Detect content type using existing method
            content_type = api_client.detect_content_type(lecture)
            stats['content_types'][content_type] += 1

            # Get asset information
            asset = lecture.get('asset', {})
            asset_type = asset.get('asset_type', 'none')
            stats['asset_types'][asset_type] += 1

            # Check for transcripts
            if asset.get('captions'):
                stats['has_transcripts'] += 1

            # Check for supplementary assets (resources)
            supp_assets = lecture.get('supplementary_assets', [])
            if supp_assets:
                stats['has_supplementary_assets'] += 1
                findings['lectures_with_resources'].append({
                    'number': lecture_num,
                    'title': lecture_title,
                    'resource_count': len(supp_assets),
                    'resources': [
                        {
                            'filename': sa.get('filename', 'Unknown'),
                            'type': sa.get('asset_type', 'Unknown'),
                            'size': sa.get('size_in_bytes', 0)
                        }
                        for sa in supp_assets
                    ]
                })
                print(f"  [{lecture_num:03d}] 📎 {lecture_title} - {len(supp_assets)} resource(s)")

            # Check for quiz data
            if 'quiz' in content_type or asset.get('quiz'):
                stats['has_quiz_data'] += 1
                findings['lectures_with_quizzes'].append({
                    'number': lecture_num,
                    'title': lecture_title,
                    'quiz_type': asset.get('quiz', {}).get('type', 'unknown')
                })
                print(f"  [{lecture_num:03d}] ❓ {lecture_title} - Quiz")

            # Check for coding exercises
            if content_type == 'coding_exercise':
                stats['has_coding_exercise'] += 1
                findings['lectures_with_coding_exercises'].append({
                    'number': lecture_num,
                    'title': lecture_title
                })
                print(f"  [{lecture_num:03d}] 💻 {lecture_title} - Coding Exercise")

            # Track promotional content
            if content_type == 'promotional':
                stats['promotional_content'] += 1

            # Store examples of each type
            if len(findings['content_type_examples'][content_type]) < 3:
                findings['content_type_examples'][content_type].append({
                    'number': lecture_num,
                    'title': lecture_title
                })

            if len(findings['asset_type_examples'][asset_type]) < 3:
                findings['asset_type_examples'][asset_type].append({
                    'number': lecture_num,
                    'title': lecture_title
                })

            lecture_num += 1

        print()  # Blank line between sections

    # Print summary
    print("=" * 60)
    print("Analysis Summary")
    print("=" * 60)
    print(f"\n📊 Overall Statistics:")
    print(f"  Total Lectures: {stats['total_lectures']}")
    print(f"  Lectures with Transcripts: {stats['has_transcripts']}")
    print(f"  Lectures with Downloadable Resources: {stats['has_supplementary_assets']}")
    print(f"  Lectures with Quizzes: {stats['has_quiz_data']}")
    print(f"  Lectures with Coding Exercises: {stats['has_coding_exercise']}")
    print(f"  Promotional Content: {stats['promotional_content']}")

    print(f"\n📝 Content Types Detected:")
    for content_type, count in sorted(stats['content_types'].items(), key=lambda x: x[1], reverse=True):
        print(f"  {content_type}: {count}")

    print(f"\n🎬 Asset Types Found:")
    for asset_type, count in sorted(stats['asset_types'].items(), key=lambda x: x[1], reverse=True):
        print(f"  {asset_type}: {count}")

    # Current vs Possible Extraction
    print(f"\n✅ Currently Extracted:")
    print(f"  - Video Transcripts: {stats['has_transcripts']} lectures")
    print(f"  - Articles: {stats['content_types']['article'] + stats['content_types']['coding_solution'] + stats['content_types']['technical_resource']} lectures")

    print(f"\n⚠️  Not Currently Extracted:")
    missing_extractions = []
    if stats['has_supplementary_assets'] > 0:
        missing_extractions.append(f"  - Downloadable Resources: {stats['has_supplementary_assets']} lectures have resources")
    if stats['has_quiz_data'] > 0:
        missing_extractions.append(f"  - Quizzes: {stats['has_quiz_data']} quiz lectures")
    if stats['has_coding_exercise'] > 0:
        missing_extractions.append(f"  - Coding Exercises: {stats['has_coding_exercise']} exercise lectures")

    if missing_extractions:
        for item in missing_extractions:
            print(item)
    else:
        print("  - None! All content types are being extracted.")

    # Recommendations
    print(f"\n💡 Implementation Recommendations:\n")

    recommendations = []

    if stats['has_supplementary_assets'] > 0:
        recommendations.append({
            'priority': 'HIGH',
            'feature': 'Resource Downloader',
            'description': f'Download and organize {stats['has_supplementary_assets']} supplementary resources (PDFs, code files, etc.)',
            'affected_lectures': stats['has_supplementary_assets'],
            'implementation': 'Already implemented in ResourceExtractor - needs activation'
        })

    if stats['has_quiz_data'] > 0:
        recommendations.append({
            'priority': 'MEDIUM',
            'feature': 'Quiz Extractor',
            'description': f'Extract quiz questions and answers from {stats['has_quiz_data']} quiz lectures',
            'affected_lectures': stats['has_quiz_data'],
            'implementation': 'Already implemented in QuizExtractor - may need API endpoint updates'
        })

    if stats['has_coding_exercise'] > 0:
        recommendations.append({
            'priority': 'MEDIUM',
            'feature': 'Coding Exercise Extractor',
            'description': f'Extract coding exercise descriptions and starter code from {stats['has_coding_exercise']} lectures',
            'affected_lectures': stats['has_coding_exercise'],
            'implementation': 'New extractor needed - investigate API endpoints'
        })

    # Sort by priority and affected lectures
    priority_order = {'HIGH': 0, 'MEDIUM': 1, 'LOW': 2}
    recommendations.sort(key=lambda x: (priority_order[x['priority']], -x['affected_lectures']))

    for idx, rec in enumerate(recommendations, 1):
        print(f"{idx}. [{rec['priority']}] {rec['feature']}")
        print(f"   Description: {rec['description']}")
        print(f"   Implementation: {rec['implementation']}\n")

    # Save detailed report
    report = {
        'course_url': course_url,
        'course_slug': course_slug,
        'statistics': dict(stats),
        'findings': {
            'lectures_with_resources': findings['lectures_with_resources'],
            'lectures_with_quizzes': findings['lectures_with_quizzes'],
            'lectures_with_coding_exercises': findings['lectures_with_coding_exercises'],
            'content_type_examples': dict(findings['content_type_examples']),
            'asset_type_examples': dict(findings['asset_type_examples'])
        },
        'recommendations': recommendations
    }

    if output_file:
        output_path = Path(output_file)
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"\n📄 Detailed report saved to: {output_path}")

    return report


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: uv run analyze_content_types.py <course_url> [output_file]")
        print("\nExample:")
        print("  uv run analyze_content_types.py https://risesmart.udemy.com/course/data-structures-and-algorithms-java content-analysis.json")
        sys.exit(1)

    course_url = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    analyze_course_content(course_url, output_file)
