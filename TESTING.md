# Testing Checklist

## Quick Test (No Google Cloud Required)

### 1. Number Validation Tests

**Aadhar Number Validation:**
- Go to `/aadhar`
- Click "Verify Number" tab
- Enter: `234567891234`
- Click "Verify Number"
- Expected: ✓ Valid Aadhar Number with confidence score

**PAN Number Validation:**
- Go to `/pan`
- Click "Verify Number" tab
- Enter: `ABCDE1234F`
- Click "Verify Number"
- Expected: ✓ Valid PAN Number with holder type "Individual"

**Invalid Tests:**
- Aadhar: `123456789012` (starts with 1) → Should fail
- PAN: `ABC123` (wrong format) → Should fail

## Full Test (Requires Google Cloud Credentials)

### 2. Image Upload Tests

**Aadhar Card Image:**
- Upload actual Aadhar card image
- Should extract number
- Should show confidence score
- Should verify keywords found

**PAN Card Image:**
- Upload actual PAN card image
- Should extract number
- Should show holder type
- Should verify keywords found

### 3. Image Resize Tests

**Aadhar/PAN Resize:**
- Go to "Resize" tab
- Upload image
- Enter width: 800, height: 600
- Select "Maintain Aspect Ratio"
- Click "Resize & Download"
- Should download resized image

**General Image Resize:**
- Go to `/resize`
- Upload any photo
- Try both resize methods
- Should download resized image

**File Size Reduction:**
- Go to `/resize`
- Click "Reduce File Size" tab
- Upload large image
- Should download compressed version
- Should show size reduction percentage

## UI/UX Tests

- [ ] Home page loads with 3 service cards
- [ ] All pages have proper gradients
- [ ] Tabs switch correctly
- [ ] Upload areas show drag & drop hint
- [ ] Image preview appears after upload
- [ ] Results show with proper colors (green/red/blue)
- [ ] Confidence bars animate
- [ ] Back links work
- [ ] Mobile responsive (test on phone)

## Error Handling Tests

- [ ] Upload without selecting file → Shows error
- [ ] Enter empty number → Shows error
- [ ] Resize without dimensions → Shows error
- [ ] Upload non-image file → Shows error
- [ ] Very large file (>16MB) → Shows error

## Browser Compatibility

- [ ] Chrome/Edge
- [ ] Firefox
- [ ] Safari
- [ ] Mobile browsers

## Deployment Tests (After deploying to Vercel)

- [ ] All routes accessible
- [ ] Static files load (CSS, JS, images)
- [ ] Google Cloud credentials work
- [ ] OCR extraction works
- [ ] File downloads work
- [ ] No console errors

---

**Let me know what issues you find and I'll fix them!**
