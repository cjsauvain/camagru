const csrfToken = document.getElementById('capture').dataset.csrfToken
const video = document.getElementById('preview')

navigator.mediaDevices.getUserMedia({ video: { width: 640, height: 480 } })
    .then(function (stream) { video.srcObject = stream })
    .catch(function () {
        video.hidden = true
        document.getElementById('preview-error').textContent =
        "Webcam unavailable. You can still upload a picture below."
    })