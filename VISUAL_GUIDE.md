# Visual Guide - What You Should See

## Success Case: Valid PDF Upload

### User Actions:
1. Click or drag a PDF file
2. Watch the progress bar

### What You'll See:

#### Upload Section
```
Progress bar: [████████████████████] 100%
Uploading: 100%
Processing complete!
```

#### Summary Section (appears)
```
📄 Document Summary
━━━━━━━━━━━━━━━━━━━━━━━━
[Document content and summary here]
```

#### Q&A Section (appears)
```
💬 Ask a Question
━━━━━━━━━━━━━━━━━━━━━━━━
[Input field] [Ask Button]
```

#### Browser Console
```
[App] File selected {name: "document.pdf", size: 2048000}
[App] Upload progress {percent: 25}
[App] Upload progress {percent: 50}
[App] Upload progress {percent: 75}
[App] Upload progress {percent: 100}
[App] Upload completed {status: 200}
[App] Document processed successfully
```

#### Flask Terminal
```
2025-12-30 14:25:45,456 - INFO - File saved: document.pdf
2025-12-30 14:25:46,789 - INFO - Processing document: document.pdf
2025-12-30 14:25:52,123 - INFO - Document processed successfully: document.pdf
```

---

## Error Case: Invalid File Type

### User Actions:
1. Click or drag a .txt, .doc, or other non-PDF file

### What You'll See:

#### Upload Section
```
Progress bar: [████████████████████] 100%
Uploading: 100%
Upload failed
```

#### Summary Section (appears with error)
```
📄 Document Summary
━━━━━━━━━━━━━━━━━━━━━━━━

❌ Error Processing Document
   Invalid file type. Please upload a PDF file.
```

#### Q&A Section (hidden)
```
[Not visible]
```

#### Browser Console
```
[App] File selected {name: "document.txt", size: 1024000}
[App] Upload completed {status: 400}
[Error] Summary processing failed Invalid file type. Please upload a PDF file.
```

#### Flask Terminal
```
2025-12-30 14:26:10,123 - WARNING - Upload attempt with non-PDF file: document.txt
```

---

## Error Case: Network Error

### User Actions:
1. Turn off internet or disconnect
2. Try to upload

### What You'll See:

#### Upload Section
```
Progress bar: [████████░░░░░░░░░░░░] 40%
[stops updating]
```

#### Summary Section (appears with error)
```
📄 Document Summary
━━━━━━━━━━━━━━━━━━━━━━━━

❌ Error Processing Document
   Network error. Please check your connection and try again.
```

#### Q&A Section (hidden)
```
[Not visible]
```

#### Browser Console
```
[App] File selected {name: "document.pdf", size: 2048000}
[App] Upload progress {percent: 40}
[Error] Upload request failed
```

---

## Q&A Success: Valid Question

### User Actions:
1. Document uploaded successfully
2. Type: "What is the main topic?"
3. Click Ask or press Enter

### What You'll See:

#### Q&A Section
```
💬 Ask a Question
━━━━━━━━━━━━━━━━━━━━━━━━
[Input field] [Ask Button]

📘 Answer:
The main topic of this document is...

Confidence: 87.5%
```

#### Browser Console
```
[App] Submitting question {question: "What is the main topic?..."}
[App] Question answered successfully
```

#### Flask Terminal
```
2025-12-30 14:27:01,456 - INFO - Processing question: What is the main topic?
2025-12-30 14:27:02,789 - INFO - Question processed successfully
```

---

## Q&A Error: Empty Question

### User Actions:
1. Click Ask without typing anything

### What You'll See:

#### Q&A Section (unchanged)
```
💬 Ask a Question
━━━━━━━━━━━━━━━━━━━━━━━━
[Input field] [Ask Button]
```

No error shown (invalid client-side, not sent to server)

#### Browser Console
```
[Warning] Empty question submitted
```

---

## Q&A Error: Server Error

### User Actions:
1. Ask a question that causes processing error
2. (e.g., malformed question structure)

### What You'll See:

#### Q&A Section
```
💬 Ask a Question
━━━━━━━━━━━━━━━━━━━━━━━━
[Input field] [Ask Button]

❌ [Error message appears here]

[Previous answer remains visible if any]
```

#### Browser Console
```
[App] Submitting question {question: "..."}
[Error] Question processing failed Network error. Please try again.
```

#### Flask Terminal
```
2025-12-30 14:28:15,789 - ERROR - Exception during question processing: [error details]
```

---

## Color Scheme Reference

### Tailwind Colors Used

**Success States:**
- Light Blue Background: `bg-blue-50`
- Blue Border: `border-blue-200`
- Dark Blue Text: `text-blue-900`
- Confidence Text: `text-blue-700`

**Error States:**
- Light Red Background: `bg-red-100`
- Red Border: `border-red-400`
- Red Text: `text-red-700`

**Default States:**
- White Background: `bg-white`
- Gray Text: `text-gray-700`
- Gray Borders: `border-gray-300`

**Interactive:**
- Blue Button: `bg-blue-600`
- Button Hover: `hover:bg-blue-700`
- Button Disabled: `disabled:bg-gray-400`
- Focus Ring: `focus:ring-2 focus:ring-blue-500`

---

## Button States

### Normal
```
[Ask Button] - Blue, clickable
```

### During Processing
```
[Ask Button] - Gray, disabled, not clickable
```

### After Answer
```
[Ask Button] - Blue, clickable again
```

---

## Progress Bar Animation

### Uploading
```
[████░░░░░░░░░░░░░░░░░░░░░░░░░░░] 20%
[██████████░░░░░░░░░░░░░░░░░░░░░░] 50%
[████████████████████░░░░░░░░░░░░] 80%
[████████████████████████████████] 100%
```

Each increment shows smooth CSS transition (0.3s)

---

## Responsive Layout Check

### Desktop (1024px+)
```
┌─────────────────────────────────────┐
│      Document Analysis System       │
├─────────────────────────────────────┤
│  Upload Section (full width)        │
├─────────────────────────────────────┤
│  Summary Section (full width)       │
├─────────────────────────────────────┤
│  Q&A Section (full width)           │
└─────────────────────────────────────┘
```

### Tablet (768px+)
```
┌──────────────────────────┐
│ Document Analysis System │
├──────────────────────────┤
│  Upload (full width)     │
├──────────────────────────┤
│  Summary (full width)    │
├──────────────────────────┤
│  Q&A (full width)        │
└──────────────────────────┘
```

### Mobile (<768px)
```
┌──────────────┐
│ Doc Analysis │
├──────────────┤
│Upload (full) │
├──────────────┤
│Summary(full) │
├──────────────┤
│Q&A (full)    │
└──────────────┘
```

---

## Common Issues & Expected Behavior

### Issue: Summary shows error, Q&A is hidden
**Expected Behavior**: ✅ Correct - Q&A only shows on success
**Action**: None needed, working as designed

### Issue: Progress bar doesn't move
**Expected Behavior**: File might be cached or too small
**Check**: Look for [App] log entries in console

### Issue: Button stays disabled
**Expected Behavior**: ❌ Problem - should re-enable after response
**Action**: Check console for JavaScript errors

### Issue: Two errors shown at once
**Expected Behavior**: ❌ Problem - should show only relevant error
**Action**: Check console logs and Flask terminal

### Issue: No console logs appearing
**Expected Behavior**: Open DevTools with F12
**Check**: Is console visible? JavaScript enabled?

---

## Accessibility Features

### Keyboard Navigation
- Tab: Move between input and button
- Enter (in input): Submit question
- Tab (to button) + Enter: Submit question

### Screen Reader Hints
- Error icons have no alt text (decorative)
- Error messages are read as text content
- Button text is clear: "Ask"
- Input placeholder: "Ask something about the document..."

### Color Not Only Indicator
- Errors have icon (❌) not just red
- Success has icon (📘) not just blue
- Messages have descriptive text

---

## Performance Indicators

### Good Performance
```
[App] Upload progress {percent: 25}  <- Every few seconds
[App] Upload completed {status: 200} <- Appears within 30 seconds
[App] Document processed successfully <- Total ~10-30 seconds
```

### Slow Performance
```
[App] Upload progress {percent: 5}   <- Every 10+ seconds
[App] Upload completed {status: 200} <- Takes >60 seconds
[App] Document processed successfully <- Total >60 seconds
```

### Check Server Logs For:
```
Processing document: document.pdf     <- Start time
Document processed successfully       <- End time
[Calculate time difference]
```
