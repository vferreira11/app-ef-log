let scene, camera, renderer, fotoTexture;
initThree();
document.getElementById('foto').addEventListener('change', upload);

function initThree() {
  scene = new THREE.Scene();
  camera = new THREE.PerspectiveCamera(45, window.innerWidth/window.innerHeight, 0.1, 1000);
  camera.position.set(0,0,5);
  renderer = new THREE.WebGLRenderer({antialias:true});
  renderer.setSize(window.innerWidth, window.innerHeight);
  document.body.appendChild(renderer.domElement);
  window.addEventListener('resize',()=> {
    camera.aspect = window.innerWidth/window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
  });
  animate();
}

function upload(ev) {
  const file = ev.target.files[0];
  const reader = new FileReader();
  reader.onload = async () => {
    const img = new Image();
    img.src = reader.result;
    await img.decode();
    // textura de fundo
    fotoTexture = new THREE.TextureLoader().load(img.src, () => {
      const bgMesh = new THREE.Mesh(
        new THREE.PlaneGeometry(4, 4 * (img.height/img.width)),
        new THREE.MeshBasicMaterial({map: fotoTexture})
      );
      bgMesh.position.set(0,0,-1);
      scene.clear();
      scene.add(bgMesh);
      detectSlots(file, img);
    });
  };
  reader.readAsDataURL(file);
}

async function detectSlots(file, img) {
  const data = new FormData();
  data.append('file', file);
  const res = await fetch('http://<SEU_IP>:8000/api/detect_slots', { method:'POST', body:data });
  const { slots } = await res.json();
  const loader = new THREE.GLTFLoader();
  for (let slot of slots) {
    // converte coords da imagem (px) para plano Three.js (-2..2,...)
    const nx = (slot.x/img.width)*4 - 2;
    const ny = 2 - (slot.y/img.height)*4*(img.height/img.width);
    const nw = (slot.w/img.width)*4;
    const nh = (slot.h/img.height)*4*(img.height/img.width);
    loader.load('models/caixa.gltf', gltf => {
      const caixa = gltf.scene;
      caixa.scale.set(nw, nh, nw);        // assume profundidade = largura
      caixa.position.set(nx + nw/2, ny - nh/2, 0);
      scene.add(caixa);
    });
  }
}

function animate() {
  requestAnimationFrame(animate);
  renderer.render(scene, camera);
}
