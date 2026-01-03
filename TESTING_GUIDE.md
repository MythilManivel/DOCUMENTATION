# Testing Guide for Updated Flask App

## Quick Start

1. Run the Flask app:
```powershell
python web_app.py
```

2. Open browser to `http://localhost:5000`

3. Open browser DevTools (F12) → Console tab to see client-side logs

## Test Scenarios

### ✅ Test 1: Successful PDF Upload
**Steps:**
1. Click upload area or select a valid PDF file
2. Observe progress bar updating from 0-100%
3. Verify summary section appears with document content
4. Verify Q&A section becomes visible

**Expected Results:**
- Progress bar shows upload percentage
- "Processing complete!" message appears
- Summary displays formatted document summary
- Q&A section is visible
- No error messages shown
- Console logs show: `[App] Document processed successfully`

**Console Output:**
```
[App] File selected {name: "document.pdf", size: 2048000}
[App] Upload progress {percent: 50}
[App] Upload completed {status: 200}
[App] Document processed successfully
```

---

### ❌ Test 2: Upload with Empty/Invalid File
**Steps:**
1. Click "Click to upload" without selecting file
2. OR drag a non-PDF file (.txt, .doc, etc.)

**Expected Results:**
- Error message appears in summary section
- Q&A section is hidden
- Red error alert with icon displays
- Console shows: `[Error] Summary processing failed`

**Console Output:**
```
[App] File selected {name: "document.txt", size: 1024000}
[App] Upload completed {status: 400}
[Error] Summary processing failed Invalid file type. Please upload a PDF file.
```

---

### ⚠️ Test 3: Network Error During Upload
**Steps:**
1. Open DevTools Network tab
2. Throttle to "Offline" mode
3. Attempt PDF upload
4. Observe error handling

**Expected Results:**
- Upload progress bar appears then stops
- Error message shows: "Network error. Please check your connection and try again."
- Summary section displays error
- Q&A section hidden
- Console shows: `[Error] Upload request failed`

---

### 💬 Test 4: Successful Q&A
**Steps:**
1. Upload valid PDF successfully
2. In question input, type a question about the document
3. Click "Ask" button or press Enter
4. Observe answer display

**Expected Results:**
- Question input clears after submission
- Answer appears in blue container
- Confidence score displays
- Button returns to enabled state
- Console shows: `[App] Question answered successfully`

---

### 📛 Test 5: Q&A Error Handling
**Steps:**
1. Upload valid PDF successfully
2. Type a question that causes an error (test with empty question)
3. Click "Ask"

**Expected Results:**
- Error alert appears in Q&A section
- Answer container remains hidden
- Red error box displays error message
- Button remains enabled for retry
- Console shows: `[Error] Question processing failed`

**Console Output:**
```
[App] Submitting question {question: "..."}
[Error] Question processing failed Network error. Please try again.
```

---

### 🔄 Test 6: Multiple Uploads in Sequence
**Steps:**
1. Upload PDF A successfully
2. Upload PDF B 
3. Upload PDF C with invalid type
4. Upload PDF D successfully

**Expected Results:**
- Each upload properly resets UI
- Progress bars work for each upload
- Summary and Q&A sections update correctly
- Error displays only when relevant
- Previous document context is cleared

---

### 📱 Test 7: UI State Validation

**Summary Section:**
- [ ] Always visible after upload attempt
- [ ] Shows content on success
- [ ] Shows error on failure
- [ ] Error has red background and icon

**Q&A Section:**
- [ ] Hidden before first upload
- [ ] Visible only after successful upload
- [ ] Hidden if upload fails
- [ ] Error alert displays separately from container

**Upload Progress:**
- [ ] Bar increases smoothly
- [ ] Percentage updates
- [ ] Shows completion message
- [ ] Stays visible until next upload

---

## Debugging Tips

### Check Server Logs
Terminal running Flask will show:
```
2025-12-30 14:25:30,123 - INFO - File saved: document.pdf
2025-12-30 14:25:31,456 - ERROR - Document processing failed: [error details]
```

### Check Client Logs
Browser Console (F12) will show:
```
[App] Upload progress {percent: 25}
[Error] Question processing failed Error details here
[Warning] Empty question submitted
```

### Common Issues

**Issue: Summary section not showing**
- Check browser console for errors
- Check Flask terminal for error logs
- Verify JSON response has `success` field

**Issue: Q&A section not appearing**
- Verify upload was successful (check console)
- Check that `document_id` is returned in response
- Verify Q&A section's hidden class is removed

**Issue: Progress bar not moving**
- Upload may be cached (clear cache)
- File may be too small to show progress
- Check Network tab in DevTools

**Issue: Errors showing as alerts instead of inline**
- Browser might be blocking console output
- Check for JavaScript errors in DevTools

---

## Performance Testing

### Load Testing
1. Upload large PDF (>10MB but <16MB limit)
2. Verify progress updates frequently
3. Monitor browser responsiveness

### Multiple Questions
1. Ask 5+ questions in succession
2. Verify each gets proper answer
3. Check for memory leaks in DevTools

---

## Manual Verification Checklist

- [ ] App starts without errors
- [ ] Upload form is accessible
- [ ] Progress bar appears during upload
- [ ] Summary appears on success
- [ ] Q&A appears on success only
- [ ] Errors shown inline (not as alerts)
- [ ] Console logging works
- [ ] Flask logs appear in terminal
- [ ] Button disabled states work
- [ ] Keyboard Enter works for questions
