const canvas = document.getElementById('canvas')
const ctx = canvas.getContext('2d')
const csrfToken = document.getElementById('capture').dataset.csrfToken
const video = document.getElementById('preview')
const button = document.getElementById('capture-button')
const upload = document.getElementById('upload')
const uploadPreview = document.getElementById('upload-preview')
const errorBox = document.getElementById('preview-error')
let webcamReady = false
let fileImage = false


async function send(pixels, overlay) {
    button.disabled = true
    errorBox.textContent = "Processing..."

    try {
        const res = await fetch('/images?overlay=' + encodeURIComponent(overlay), {
            method: 'POST',
            headers: {
                'Content-Type': 'application/octet-stream',
                'X-CSRF-Token': csrfToken
            },
            body: pixels
        })

        if (res.status === 201) {
            location.reload()
            return
        } else if (res.status === 403) {
            errorBox.textContent = "Session expired, please reload the page."
        } else {
            errorBox.textContent = await res.text()
        }
    } catch (err) {
        errorBox.textContent = "Network error, please try again."
    }

    updateButton()
}


function selectedOverlay() {
    const checked = document.querySelector('input[name="overlay"]:checked')
    return checked ? checked.value : null
}


function updateButton() {
    button.disabled = !(selectedOverlay() && (webcamReady || fileImage))
}


navigator.mediaDevices.getUserMedia({ video: { width: 640, height: 480 } })
    .then(function (stream) { video.srcObject = stream })
    .catch(function () {
        video.hidden = true
        errorBox.textContent = "Webcam unavailable. You can still upload a picture below."
    })
document.querySelectorAll('input[name="overlay"]').forEach(function (radio) {
    radio.addEventListener('change', updateButton)
})
video.addEventListener('playing', function () {
    webcamReady = true
    updateButton()
})
button.addEventListener('click', function () {
    const source = fileImage ? uploadPreview : video
    ctx.drawImage(source, 0, 0, 640, 480)
    const pixels = ctx.getImageData(0, 0, 640, 480).data
    send(pixels, selectedOverlay())
})
upload.addEventListener('change', function () {
    const file = upload.files[0]
    if (!file) return
    uploadPreview.src = URL.createObjectURL(file)
})
uploadPreview.addEventListener('load', function() {
    uploadPreview.hidden = false
    video.hidden = true
    fileImage = true
    errorBox.textContent = ""
    updateButton()
})
uploadPreview.addEventListener('error', function() {
    uploadPreview.hidden = true
    video.hidden = !webcamReady
    errorBox.textContent = "This file is not a valid image."
    fileImage = false
    updateButton()
})