const csrfToken = document.getElementById('capture').dataset.csrfToken
const video = document.getElementById('preview')
const button = document.getElementById('capture-button')
const errorBox = document.getElementById('preview-error')
let webcamReady = false


function selectedOverlay() {
    const checked = document.querySelector('input[name="overlay"]:checked')
    return checked ? checked.value : null
}


function updateButton() {
    button.disabled = !(selectedOverlay() && webcamReady)
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
