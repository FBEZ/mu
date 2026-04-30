# OLX Course Data Location Guide

This document provides instructions on where to add course picture, video, description, and start date in an OLX course structure.

---

## 1. Course Picture

### Where to Add:
**File**: `course/2026_T1.xml` (or `course/<your_course_run>.xml`)

**Attribute**: `course_image` in the `<course>` element

**Example**:
```xml
<course course_image="collage_1_.png" display_name="ESP-IDF Basic" start="2029-12-31T00:00:00Z">
```

### Image File Location:
**Directory**: `static/`

**Current File**: `static/collage(1).png`

**Instructions**:
- Place your course image file in the `static/` folder
- Reference the filename in the `course_image` attribute
- Supported formats: PNG, JPG, JPEG
- Recommended size: 2120 x 1192 pixels (16:9 aspect ratio)

**Note**: Ensure the filename in XML matches the actual file in the static folder (currently there's a mismatch: XML references `collage_1_.png` but file is named `collage(1).png`)

---

## 2. Course Video (About/Promo Video)

### Where to Add:
**File**: `about/video.html`

**Format**: HTML iframe embed (typically YouTube or other video platform)

**Current Content**:
```html
<iframe title="YouTube Video" width="560" height="315" src="//www.youtube.com/embed/https://www.youtube.com/watch?v=gNMMuoTvSBc?rel=0" frameborder="0" allowfullscreen=""></iframe>
```

**Correct Format**:
```html
<iframe title="YouTube Video" width="560" height="315" src="//www.youtube.com/embed/VIDEO_ID?rel=0" frameborder="0" allowfullscreen=""></iframe>
```

**Instructions**:
- Replace `VIDEO_ID` with your YouTube video ID
- For YouTube video `https://www.youtube.com/watch?v=gNMMuoTvSBc`, the ID is `gNMMuoTvSBc`
- The embed URL should be: `//www.youtube.com/embed/gNMMuoTvSBc?rel=0`

---

## 3. Course Description

### 3.1 Short Description
**File**: `about/short_description.html`

**Current Content**: 
```
This is a short course about the course
```

**Instructions**:
- Add a brief one-liner description (typically 1-2 sentences)
- This appears in course listings and search results
- Plain text format (no HTML tags needed)
- Maximum recommended length: 150 characters

---

### 3.2 Course Overview
**File**: `about/overview.html`

**Current Content**:
```html
<h2><strong>Kanu kanu</strong></h2>
<p><strong></strong></p>
<p><strong>This is a course!</strong></p>
<p><strong></strong></p>
<p><strong>ODOD</strong></p>
```

**Instructions**:
- Add detailed HTML-formatted course overview
- This appears on the course About page
- Can include: headings, paragraphs, lists, images, links
- Typical sections:
  - Course overview/introduction
  - What you'll learn
  - Prerequisites
  - Course structure
  - Instructor information

---

### 3.3 Full Description
**File**: `about/description.html`

**Current Status**: Empty

**Instructions**:
- Add comprehensive course description (if needed)
- Similar to overview but may be used differently depending on platform
- HTML format supported

---

### 3.4 Other Description Files

**File**: `about/title.html`
- Course title (currently empty)

**File**: `about/subtitle.html`
- Course subtitle (currently empty)

**File**: `about/effort.html`
- Expected effort per week (e.g., "5-7 hours per week")
- Current content: `5-7`

**File**: `about/duration.html`
- Course duration (e.g., "6 weeks")
- Currently empty

---

## 4. Start Date

### Where to Add:
**File**: `course/2026_T1.xml` (or `course/<your_course_run>.xml`)

**Attribute**: `start` in the `<course>` element

**Current Value**: `2029-12-31T00:00:00Z`

**Format**: ISO 8601 datetime format (UTC timezone)

**Example**:
```xml
<course start="2029-12-31T00:00:00Z" display_name="ESP-IDF Basic">
```

**Instructions**:
- Format: `YYYY-MM-DDTHH:MM:SSZ`
- Always use UTC timezone (Z suffix)
- Date: December 31, 2029 at midnight UTC

**Examples**:
- January 15, 2026: `2026-01-15T00:00:00Z`
- March 1, 2026, 9:00 AM UTC: `2026-03-01T09:00:00Z`
- June 30, 2027: `2027-06-30T00:00:00Z`

---

## Complete Course Metadata Example

**File**: `course/2026_T1.xml`

```xml
<course 
  certificates_display_behavior="CertificatesDisplayBehaviors.END" 
  course_image="collage_1_.png" 
  display_name="ESP-IDF Basic" 
  instructor_info="{&quot;instructors&quot;: []}" 
  language="ak" 
  learning_info="[]" 
  start="2029-12-31T00:00:00Z">
  <chapter url_name="cfcd208495d565ef66e7dff9f98764da"/>
  <chapter url_name="c4ca4238a0b923820dcc509a6f75849b"/>
  <chapter url_name="c81e728d9d4c2f636f067f89cc14862c"/>
  <wiki slug="Espressif.CC0001.2026_T1"/>
</course>
```

---

## Course Structure Summary

```
course 5/
├── course.xml                          # Root course reference
├── course/
│   └── 2026_T1.xml                    # Main course metadata (picture, start date, title)
├── about/
│   ├── video.html                     # Course promo video
│   ├── short_description.html         # Brief description
│   ├── overview.html                  # Detailed overview (HTML)
│   ├── description.html               # Full description
│   ├── title.html                     # Course title
│   ├── subtitle.html                  # Course subtitle
│   ├── effort.html                    # Weekly effort estimate
│   └── duration.html                  # Course duration
└── static/
    └── collage(1).png                 # Course image file
```

---

## Current Issues Found

1. **Filename Mismatch**: 
   - XML references: `collage_1_.png`
   - Actual file: `collage(1).png`
   - **Fix**: Rename file or update XML reference

2. **Video Embed URL Issue**:
   - Current: `src="//www.youtube.com/embed/https://www.youtube.com/watch?v=gNMMuoTvSBc?rel=0"`
   - Should be: `src="//www.youtube.com/embed/gNMMuoTvSBc?rel=0"`
   - **Fix**: Remove the full URL and use only the video ID

---

## Additional Course Information Found

- **Course Title**: ESP-IDF Basic
- **Organization**: Espressif
- **Course Code**: CC0001
- **Course Run**: 2026_T1
- **Language**: ak (Akan)
- **Start Date**: December 31, 2029

---

*Generated from OLX course structure analysis on April 30, 2026*
