import * as THREE from "https://cdn.jsdelivr.net/npm/three@0.170.0/build/three.module.js";

const canvas = document.getElementById("flower3d");

if (canvas) {
    const scene = new THREE.Scene();
    scene.fog = new THREE.FogExp2(0x050706, 0.045);

    const camera = new THREE.PerspectiveCamera(48, 1, 0.1, 80);
    camera.position.set(0, 0.2, 8);

    const renderer = new THREE.WebGLRenderer({
        canvas,
        alpha: true,
        antialias: true
    });

    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.5));
    renderer.outputColorSpace = THREE.SRGBColorSpace;

    scene.add(new THREE.AmbientLight(0xffffff, 1.3));

    const moonLight = new THREE.PointLight(0xffffff, 35, 25);
    moonLight.position.set(0, 4, 1);
    scene.add(moonLight);

    const gardenLight = new THREE.PointLight(0xffa45b, 45, 20);
    gardenLight.position.set(0, 0, -7);
    scene.add(gardenLight);

    // Dark garden floor
    const ground = new THREE.Mesh(
        new THREE.PlaneGeometry(35, 35),
        new THREE.MeshStandardMaterial({
            color: 0x101b13,
            roughness: 0.95
        })
    );

    ground.rotation.x = -Math.PI / 2;
    ground.position.set(0, -2.6, -7);
    scene.add(ground);

    // Glowing circular portal
    const portal = new THREE.Group();
    portal.position.set(0, 0.1, -8);
    scene.add(portal);

    const ring = new THREE.Mesh(
        new THREE.TorusGeometry(1.25, 0.045, 16, 100),
        new THREE.MeshStandardMaterial({
            color: 0xffbd78,
            emissive: 0xff682a,
            emissiveIntensity: 3,
            metalness: 0.5
        })
    );

    portal.add(ring);

    const innerRing = new THREE.Mesh(
        new THREE.TorusGeometry(1.15, 0.012, 8, 100),
        new THREE.MeshBasicMaterial({
            color: 0xffd8a3
        })
    );

    portal.add(innerRing);

    // Flower materials
    const petalGeometry = new THREE.SphereGeometry(1, 12, 10);

    const petalMaterials = [
        new THREE.MeshStandardMaterial({
            color: 0xff8ba5,
            emissive: 0x4d1022,
            emissiveIntensity: 0.4,
            roughness: 0.45
        }),
        new THREE.MeshStandardMaterial({
            color: 0xffa45c,
            emissive: 0x4d1c05,
            emissiveIntensity: 0.5
        }),
        new THREE.MeshStandardMaterial({
            color: 0xffd66e,
            emissive: 0x493000,
            emissiveIntensity: 0.4
        }),
        new THREE.MeshStandardMaterial({
            color: 0xf2d5e8,
            emissive: 0x321827,
            emissiveIntensity: 0.3
        })
    ];

    const centreMaterial = new THREE.MeshStandardMaterial({
        color: 0xffd77c,
        emissive: 0xff8a27,
        emissiveIntensity: 1.5
    });

    const stemMaterial = new THREE.MeshStandardMaterial({
        color: 0x294b2e
    });

    const flowerGroups = [];

    function createFlower(x, y, z, scale, colorIndex) {
        const flower = new THREE.Group();

        const material = petalMaterials[colorIndex];

        // Six curved-looking petals
        for (let i = 0; i < 6; i++) {
            const angle = i * Math.PI / 3;

            const petal = new THREE.Mesh(
                petalGeometry,
                material
            );

            petal.scale.set(0.17, 0.36, 0.09);
            petal.position.set(
                Math.sin(angle) * 0.23,
                Math.cos(angle) * 0.23,
                0
            );

            petal.rotation.z = -angle;
            flower.add(petal);
        }

        const centre = new THREE.Mesh(
            new THREE.SphereGeometry(0.13, 16, 16),
            centreMaterial
        );

        centre.position.z = 0.08;
        flower.add(centre);

        // Stem
        const stem = new THREE.Mesh(
            new THREE.CylinderGeometry(0.018, 0.035, 1.25, 7),
            stemMaterial
        );

        stem.position.y = -0.85;
        flower.add(stem);

        // Leaves
        for (let i = 0; i < 2; i++) {
            const leaf = new THREE.Mesh(
                petalGeometry,
                stemMaterial
            );

            leaf.scale.set(0.12, 0.32, 0.045);
            leaf.position.set(i === 0 ? 0.18 : -0.18, -0.65, 0);
            leaf.rotation.z = i === 0 ? -1 : 1;
            flower.add(leaf);
        }

        flower.position.set(x, y, z);
        flower.scale.setScalar(scale);

        scene.add(flower);
        flowerGroups.push(flower);

        return flower;
    }

    // Build the flower tunnel along both garden edges
    for (let i = 0; i < 55; i++) {
        const side = i % 2 === 0 ? -1 : 1;

        const x = side * (2.3 + Math.random() * 2.5);
        const y = -1.5 + Math.random() * 2.1;
        const z = -1 - Math.random() * 12;

        createFlower(
            x,
            y,
            z,
            0.35 + Math.random() * 0.65,
            Math.floor(Math.random() * 4)
        );
    }

    // Flowers surrounding the portal
    for (let i = 0; i < 9; i++) {
        const angle = i * Math.PI * 2 / 9;

        createFlower(
            Math.cos(angle) * 1.4,
            Math.sin(angle) * 1.3,
            -7.4,
            0.5 + Math.random() * 0.25,
            i % 4
        );
    }

    // Floating fireflies
    const fireflies = [];

    for (let i = 0; i < 85; i++) {
        const light = new THREE.Mesh(
            new THREE.SphereGeometry(0.025, 6, 6),
            new THREE.MeshBasicMaterial({
                color: i % 3 === 0 ? 0xffd68a : 0xffffff
            })
        );

        light.position.set(
            (Math.random() - 0.5) * 10,
            (Math.random() - 0.5) * 5,
            -Math.random() * 12
        );

        scene.add(light);

        fireflies.push({
            mesh: light,
            speed: 0.003 + Math.random() * 0.006,
            phase: Math.random() * 6
        });
    }

    // Responsive layout
    function resize() {
        const width = canvas.clientWidth;
        const height = canvas.clientHeight;

        if (!width || !height) return;

        camera.aspect = width / height;
        camera.updateProjectionMatrix();

        renderer.setSize(width, height, false);
    }

    const observer = new ResizeObserver(resize);
    observer.observe(canvas);
    resize();

    let mouseX = 0;
    let mouseY = 0;

    window.addEventListener("pointermove", (event) => {
        mouseX = (event.clientX / window.innerWidth - 0.5) * 0.3;
        mouseY = (event.clientY / window.innerHeight - 0.5) * 0.15;
    });

    const clock = new THREE.Clock();

    function animate() {
        requestAnimationFrame(animate);

        const t = clock.getElapsedTime();

        portal.rotation.z = Math.sin(t * 0.2) * 0.025;

        camera.position.x += (mouseX - camera.position.x) * 0.025;
        camera.position.y += (0.2 - mouseY - camera.position.y) * 0.025;

        flowerGroups.forEach((flower, i) => {
            flower.rotation.z =
                Math.sin(t * 0.7 + i) * 0.035;
        });

        fireflies.forEach((item) => {
            item.mesh.position.y += item.speed;
            item.mesh.position.x += Math.sin(t + item.phase) * 0.001;

            if (item.mesh.position.y > 3) {
                item.mesh.position.y = -3;
            }
        });

        renderer.render(scene, camera);
    }

    animate();
}
