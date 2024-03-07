<script type="module">
      import {
        Camera,
        DirectionalLight,
        Color,
        Material,
        PointLight,
        WebGLRenderer,
        Scene,
        PerspectiveCamera,
        Texture,
        AmbientLight,
      } from 'https://unpkg.com/three@0.120.1/build/three.module.js'
      import { OrbitControls } from 'https://unpkg.com/three@0.120.1/examples/jsm/controls/OrbitControls.js'
      import { GLTFLoader } from 'https://unpkg.com/three@0.120.1/examples/jsm/loaders/GLTFLoader.js'

      let scene, camera, renderer;

      function init() {

        scene = new Scene();
        scene.background = new Color(0xdddddd);

        camera = new PerspectiveCamera(40,window.innerWidth/window.innerHeight,1,5000);
        camera.rotation.y = 45/180*Math.PI;
        camera.position.x = 8;
        camera.position.y = 1;
        camera.position.z = 10;

        const hlight = new AmbientLight (0x404040,100);
        scene.add(hlight);

        const directionalLight = new DirectionalLight(0xffffff,100);
        directionalLight.position.set(0,1,0);
        directionalLight.castShadow = true;
        scene.add(directionalLight);
        const light = new PointLight(0xc4c4c4,10);
        light.position.set(0,300,500);
        scene.add(light);
        const light2 = new PointLight(0xc4c4c4,10);
        light2.position.set(500,100,0);
        scene.add(light2);
        const light3 = new PointLight(0xc4c4c4,10);
        light3.position.set(0,100,-500);
        scene.add(light3);
        const light4 = new PointLight(0xc4c4c4,10);
        light4.position.set(-500,300,500);
        scene.add(light4);

        renderer = new WebGLRenderer({antialias:true});
        renderer.setSize(window.innerWidth,window.innerHeight);
        document.body.appendChild(renderer.domElement);

        const controls = new OrbitControls(camera, renderer.domElement);
        // controls.addEventListener('change', renderer);

        let loader = new GLTFLoader();
        loader.load(<script type="module">
      import {
        Camera,
        DirectionalLight,
        Color,
        Material,
        PointLight,
        WebGLRenderer,
        Scene,
        PerspectiveCamera,
        Texture,
        AmbientLight,
      } from 'https://unpkg.com/three@0.120.1/build/three.module.js'
      import { OrbitControls } from 'https://unpkg.com/three@0.120.1/examples/jsm/controls/OrbitControls.js'
      import { GLTFLoader } from 'https://unpkg.com/three@0.120.1/examples/jsm/loaders/GLTFLoader.js'

      let scene, camera, renderer;

      function init() {

        scene = new Scene();
        scene.background = new Color(0xdddddd);

        camera = new PerspectiveCamera(40,window.innerWidth/window.innerHeight,1,5000);
        camera.rotation.y = 45/180*Math.PI;
        camera.position.x = 8;
        camera.position.y = 1;
        camera.position.z = 10;

        const hlight = new AmbientLight (0x404040,100);
        scene.add(hlight);

        const directionalLight = new DirectionalLight(0xffffff,100);
        directionalLight.position.set(0,1,0);
        directionalLight.castShadow = true;
        scene.add(directionalLight);
        const light = new PointLight(0xc4c4c4,10);
        light.position.set(0,300,500);
        scene.add(light);
        const light2 = new PointLight(0xc4c4c4,10);
        light2.position.set(500,100,0);
        scene.add(light2);
        const light3 = new PointLight(0xc4c4c4,10);
        light3.position.set(0,100,-500);
        scene.add(light3);
        const light4 = new PointLight(0xc4c4c4,10);
        light4.position.set(-500,300,500);
        scene.add(light4);

        renderer = new WebGLRenderer({antialias:true});
        renderer.setSize(window.innerWidth,window.innerHeight);
        document.body.appendChild(renderer.domElement);

        const controls = new OrbitControls(camera, renderer.domElement);
        // controls.addEventListener('change', renderer);

        let loader = new GLTFLoader();
        loader.load('{{ url_for("static", filename="uploads/" + product.three_d_view) }}', function(gltf){
          const car = gltf.scene.children[0];
          console.log('car: ', car);
          car.scale.set(0.5,0.5,0.5);
          scene.add(car);
          animate();
        });
      }
      function animate() {
        renderer.render(scene,camera);
        requestAnimationFrame(animate);
      }
      init();
    </script>, function(gltf){
          const car = gltf.scene.children[0];
          console.log('car: ', car);
          car.scale.set(0.5,0.5,0.5);
          scene.add(car);
          animate();
        });
      }
      function animate() {
        renderer.render(scene,camera);
        requestAnimationFrame(animate);
      }
      init();
    </script>

(venv)$ export STRIPE_PUBLISHABLE_KEY=pk_test_VOOyyYjgzqdm8I3SrBqmh9qY
(venv)$ export STRIPE_SECRET_KEY=sk_test_Gx4mWEgHtCMr4DYMUIqfIrsz
(env)$ export STRIPE_ENDPOINT_SECRET=<YOUR_ENDPOINT_SECRET_KEY>