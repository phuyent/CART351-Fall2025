//Javascript for website
//import THREE.js library
import * as THREE from 'https://cdn.skypack.dev/three@0.129.0/build/three.module.js';
//import GLTF library to be able to read glb files format
import { GLTFLoader } from 'https://cdn.skypack.dev/three@0.129.0/examples/jsm/loaders/GLTFLoader.js';
//import gsap library for animation transition
import { gsap } from 'https://cdn.skypack.dev/gsap';

//set up camera
const camera = new THREE.PerspectiveCamera(
    10, //viewing angle
    window.innerWidth / window.innerHeight, //frame ratio
    0.1, //closest distance camera can see
    1000 //farthest distance camera can see
);
//camera position: move z axis to see the whole scene
camera.position.z = 13;
//setting the scene 
const scene = new THREE.Scene();
let butterfly;

//add a variable to manage 3d animation
let mixer;
//use load method to get 3d model file
const loader = new GLTFLoader();
loader.load('/12_animated_butterflies.glb',
    //1st callback function runs when loading is done
    function (gltf) {
        butterfly = gltf.scene;
        scene.add(butterfly);
        console.log(gltf.animations);

        mixer = new THREE.AnimationMixer(butterfly);
        //declare the main animation at 0 is the one moving
        mixer.clipAction(gltf.animations[0]).play();
        modelMove();
    },
    //2nd callback function is always running to check file loading progress
    function (xhr) {},
    //3rd callback funtion to report errors during loading process
    function (error) {}
);
//create canvas the size of the screen window
const renderer = new THREE.WebGLRenderer({alpha: true}); //transparent color background
renderer.setSize(window.innerWidth, window.innerHeight);
document.getElementById('container3D').appendChild(renderer.domElement);

//whenever loading the 3d file is done, this function will continously render new data
const reRender3D = () => {
    requestAnimationFrame(reRender3D);
    renderer.render(scene, camera);
    if(mixer) mixer.update(0.02); //continuously update animation
};
reRender3D();

//adding light to the 3d model
//ambient light for even distribution of the light, therefore show whole color of 3d model
const ambientLight = new THREE.AmbientLight(0xffffff, 1.3); //white light and intensity values of lighting
scene.add(ambientLight);
//directional light for highlights and shadows on 3d model
const topLight = new THREE.DirectionalLight(0xffffff, 1); //white light and intensity values of lighting
topLight.position.set(500, 500, 500);
scene.add(topLight);
//an array of different positions for each section when scrolling
//each section is identified by its unique ID in HTML
let arrPositionModel = [
    {
        id: 'banner',
        position: {x: 0, y: -1, z: 0},
        rotation: {x: 0, y: 1.5, z: 0}
    },
    {
        id: "exercises",
        position: { x: -2, y: -1, z: -5 },
        rotation: { x: 0, y: 0.5, z: 0 },
    },
    {
        id: "projects",
        position: { x: 2, y: -1, z: -5 },
        rotation: { x: 0.5, y: -0.5, z: 0 },
    },
    {
        id: "end",
        position: {x: 0, y: -1, z: 0},
        rotation: { x: 0.3, y: -0.5, z: 0 },
    },
];

const modelMove = () => {
    const sections = document.querySelectorAll('.section');
    let currentSection;
    //get current position of each section
    sections.forEach((section) => {
        const rect = section.getBoundingClientRect(); 
    //if current distance is less than 1/3 of screen's height, then the current position = id's section
        if (rect.top <= window.innerHeight / 3) {
            currentSection = section.id;
        }
    });
    //use findIndex() to find its corresponding position in the array if the id value matches
    let position_active = arrPositionModel.findIndex(
        (val) => val.id == currentSection
    );
    //if the found or active position is greater or equal to 0, new coordinates = 3d object's new position
    if (position_active >= 0) {
        let new_coordinates = arrPositionModel[position_active];
        //use gsap to smoothly transition to new coordinates
        gsap.to(butterfly.position, {
            x: new_coordinates.position.x,
            y: new_coordinates.position.y,
            z: new_coordinates.position.z,
            //transition quickly 
            duration: 2,
            
        });
        //gsap can also change rotation of 3d model
        gsap.to(butterfly.rotation, {
            x: new_coordinates.rotation.x,
            y: new_coordinates.rotation.y,
            z: new_coordinates.rotation.z,
            duration: 2,
           
        })
    }
}
//capture user's scroll event
window.addEventListener('scroll', () => {
    if (butterfly) {
        modelMove();
    }
})
//make the website and 3d model responsive to any screen size
window.addEventListener('resize', () => {
    renderer.setSize(window.innerWidth, window.innerHeight);
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
})