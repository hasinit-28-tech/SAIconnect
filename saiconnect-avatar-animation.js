
import * as THREE from "https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js";
import { GLTFLoader } from "https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/loaders/GLTFLoader.js";

// =====================================
// SAI CONNECT - VIRTUAL RECEPTIONIST
// =====================================

const canvas = document.getElementById("avatarCanvas");
const loadingElement = document.getElementById("avatarLoading");

if (!canvas) {
    console.error("Avatar canvas not found!");
    throw new Error("Missing #avatarCanvas in index.html");
}

// =====================================
// SCENE
// =====================================

const scene = new THREE.Scene();
scene.background = new THREE.Color(0xf3f5fa);

const camera = new THREE.PerspectiveCamera(
    35,
    1,
    0.1,
    100
);

camera.position.set(0, 1.55, 5.2);
camera.lookAt(0, 1.45, 0);

// =====================================
// RENDERER
// =====================================

const renderer = new THREE.WebGLRenderer({
    canvas,
    antialias: true,
    alpha: true
});

renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.1;

// =====================================
// LIGHTING
// =====================================

scene.add(new THREE.AmbientLight(0xffffff, 1.5));

const keyLight = new THREE.DirectionalLight(0xffffff, 2.2);
keyLight.position.set(2, 4, 5);
scene.add(keyLight);

const fillLight = new THREE.DirectionalLight(0xdce8ff, 1);
fillLight.position.set(-3, 2, 2);
scene.add(fillLight);

const rimLight = new THREE.DirectionalLight(0xffffff, 1.5);
rimLight.position.set(0, 3, -3);
scene.add(rimLight);

// =====================================
// AVATAR VARIABLES
// =====================================

let avatar = null;
let headBone = null;
let neckBone = null;

const morphTargets = [];

let isSpeaking = false;
let isSmiling = false;
let isBlinking = false;

let blinkValue = 0;
let nextBlinkTime = 2;
let blinkStartTime = 0;

const clock = new THREE.Clock();

// =====================================
// RESPONSIVE SIZE
// =====================================

function resizeAvatar() {
    const width = canvas.clientWidth;
    const height = canvas.clientHeight;

    if (!width || !height) return;

    camera.aspect = width / height;
    camera.updateProjectionMatrix();

    renderer.setSize(width, height, false);
}

resizeAvatar();

window.addEventListener("resize", resizeAvatar);

if ("ResizeObserver" in window) {
    const observer = new ResizeObserver(resizeAvatar);
    observer.observe(canvas);
}

// =====================================
// LOAD AVATAR MODEL
// =====================================

const loader = new GLTFLoader();

console.log("Loading SAIConnect avatar...");

loader.load(
    new URL("./avatar.glb", import.meta.url).href,

    (gltf) => {
        avatar = gltf.scene;

        const box = new THREE.Box3().setFromObject(avatar);
        const size = new THREE.Vector3();
        const center = new THREE.Vector3();

        box.getSize(size);
        box.getCenter(center);

        if (!size.y) {
            console.error("Avatar model has invalid dimensions.");
            return;
        }

        const desiredHeight = 3;
        const scale = desiredHeight / size.y;

        avatar.scale.setScalar(scale);

        avatar.position.x = -center.x * scale;
        avatar.position.y = -box.min.y * scale;
        avatar.position.z = -center.z * scale;

        scene.add(avatar);

        // Find bones and facial morph targets
        avatar.traverse((object) => {

            if (object.isSkinnedMesh && object.morphTargetDictionary) {
                morphTargets.push(object);

                console.log(
                    "Morph targets:",
                    object.name,
                    Object.keys(object.morphTargetDictionary)
                );
            }

            if (object.isBone) {
                const boneName = object.name.toLowerCase();

                if (
                    !headBone &&
                    boneName.includes("head")
                ) {
                    headBone = object;
                }

                if (
                    !neckBone &&
                    boneName.includes("neck")
                ) {
                    neckBone = object;
                }
            }
        });

        console.log("Avatar loaded successfully!");
        console.log("Head bone:", headBone?.name);
        console.log("Neck bone:", neckBone?.name);

        if (loadingElement) {
            loadingElement.style.display = "none";
        }

        setSmile(0.15);
        resizeAvatar();
    },

    (progress) => {
        if (progress.total > 0 && loadingElement) {
            const percentage = Math.round(
                (progress.loaded / progress.total) * 100
            );

            loadingElement.textContent =
                `Loading your university assistant... ${percentage}%`;

            console.log(`Avatar loading: ${percentage}%`);
        }
    },

    (error) => {
        console.error("Could not load avatar.glb:", error);

        if (loadingElement) {
            loadingElement.textContent =
                "Unable to load avatar. Check the browser console.";
        }
    }
);

// =====================================
// FACIAL ANIMATION HELPERS
// =====================================

function setMorph(name, value) {
    morphTargets.forEach((mesh) => {
        const index = mesh.morphTargetDictionary?.[name];

        if (
            index !== undefined &&
            mesh.morphTargetInfluences
        ) {
            mesh.morphTargetInfluences[index] =
                THREE.MathUtils.clamp(value, 0, 1);
        }
    });
}

function setSmile(value) {
    setMorph("mouthSmileLeft", value);
    setMorph("mouthSmileRight", value);
}

function setBlink(value) {
    setMorph("eyeBlinkLeft", value);
    setMorph("eyeBlinkRight", value);
}

// =====================================
// NATURAL BLINKING
// =====================================

function updateBlink(elapsed) {

    if (!isBlinking && elapsed >= nextBlinkTime) {
        isBlinking = true;
        blinkStartTime = elapsed;
    }

    if (isBlinking) {
        const duration = elapsed - blinkStartTime;

        if (duration < 0.12) {
            blinkValue = duration / 0.12;
        } else if (duration < 0.24) {
            blinkValue = 1 - (duration - 0.12) / 0.12;
        } else {
            blinkValue = 0;
            isBlinking = false;
            nextBlinkTime = elapsed + 2 + Math.random() * 4;
        }

        setBlink(blinkValue);
    }
}

// =====================================
// SPEAKING / LIP-SYNC ANIMATION
// =====================================

function updateMouth(elapsed) {

    if (isSpeaking) {

        const jaw =
            0.15 + Math.abs(Math.sin(elapsed * 12)) * 0.45;

        const funnel =
            Math.abs(Math.sin(elapsed * 8)) * 0.25;

        setMorph("jawOpen", jaw);
        setMorph("mouthFunnel", funnel);

        setSmile(0.08);

    } else {

        setMorph("jawOpen", 0);
        setMorph("mouthFunnel", 0);

        setSmile(isSmiling ? 0.3 : 0.12);
    }
}

// =====================================
// FEMALE VOICE
// =====================================

function getPreferredVoice() {

    if (!("speechSynthesis" in window)) {
        return null;
    }

    const voices = window.speechSynthesis.getVoices();

    return (
        voices.find(
            voice => voice.name === "Google UK English Female"
        ) ||
        voices.find(
            voice => voice.name.includes("Microsoft Zira")
        ) ||
        null
    );
}

// =====================================
// SPEAK FUNCTION
// =====================================

function speak(text) {

    if (!text || !("speechSynthesis" in window)) {
        return;
    }

    window.speechSynthesis.cancel();

    const voice = getPreferredVoice();

    if (!voice) {
        console.warn("Preferred female voice is unavailable.");
        return;
    }

    const utterance = new SpeechSynthesisUtterance(text);

    utterance.voice = voice;
    utterance.lang = voice.lang;
    utterance.rate = 0.92;
    utterance.pitch = 1.05;
    utterance.volume = 1;

    utterance.onstart = () => {
        isSpeaking = true;
    };

    utterance.onend = () => {
        isSpeaking = false;
    };

    utterance.onerror = (event) => {
        console.error("Speech error:", event.error);
        isSpeaking = false;
    };

    window.speechSynthesis.speak(utterance);
}

// =====================================
// STOP SPEAKING
// =====================================

function stopSpeaking() {

    if ("speechSynthesis" in window) {
        window.speechSynthesis.cancel();
    }

    isSpeaking = false;
}

// =====================================
// SMILE CONTROLS
// =====================================

function smile() {
    isSmiling = true;
    setSmile(0.3);
}

function relaxFace() {
    isSmiling = false;
}

// =====================================
// EXPOSE AVATAR FUNCTIONS
// =====================================

window.SAIAvatar = {

    speak,

    stopSpeaking,

    smile,

    relaxFace,

    setSpeaking(value) {
        isSpeaking = Boolean(value);
    }

};

// =====================================
// ANIMATION LOOP
// =====================================

function animate() {

    requestAnimationFrame(animate);

    const elapsed = clock.getElapsedTime();

    if (avatar) {

        // Gentle body movement
        avatar.position.y += Math.sin(elapsed * 1.5) * 0.0008;

        // Gentle idle rotation
        avatar.rotation.y = Math.sin(elapsed * 0.5) * 0.035;

        // Head movement
        if (headBone) {
            headBone.rotation.y =
                Math.sin(elapsed * 0.7) * 0.06;

            headBone.rotation.x =
                Math.sin(elapsed * 0.9) * 0.025;
        }

        // Neck movement
        if (neckBone) {
            neckBone.rotation.y =
                Math.sin(elapsed * 0.6) * 0.025;
        }

        updateBlink(elapsed);
        updateMouth(elapsed);
    }

    renderer.render(scene, camera);
}

animate();

console.log("SAIConnect avatar animation initialized!");