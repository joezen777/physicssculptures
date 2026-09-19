import React,{useEffect,useRef} from 'react';
import * as THREE from 'three';
import {OrbitControls} from 'three/addons/controls/OrbitControls.js';

export default function Scene({state,model}) {
  const host=useRef(null), live=useRef(state), sceneRef=useRef(null);
  live.current=state;
  useEffect(()=>{
    const scene=new THREE.Scene(); scene.background=new THREE.Color('#101a28');
    const camera=new THREE.PerspectiveCamera(40,1,.01,100);
    camera.up.set(0,0,1); camera.position.set(1.5,-1.9,2.15);
    const renderer=new THREE.WebGLRenderer({antialias:true});
    renderer.setPixelRatio(Math.min(window.devicePixelRatio,2));
    renderer.setClearColor('#101a28');
    renderer.outputColorSpace=THREE.SRGBColorSpace;
    host.current.appendChild(renderer.domElement);
    const controls=new OrbitControls(camera,renderer.domElement);
    controls.target.set(0,0,1.12); controls.enableDamping=true;
    scene.add(new THREE.HemisphereLight(0xd8f1ff,0x1b2834,2.4));
    const sun=new THREE.DirectionalLight(0xffffff,3.2); sun.position.set(2,-3,5);scene.add(sun);
    const fill=new THREE.DirectionalLight(0x77d9d1,1.6);fill.position.set(-3,2,3);scene.add(fill);
    const grid=new THREE.GridHelper(8,40,0x42536b,0x23334b);
    grid.rotation.x=Math.PI/2;scene.add(grid);
    const axes=new THREE.AxesHelper(.18); axes.position.set(-.65,-.65,.01); scene.add(axes);
    const machine=new THREE.Group();scene.add(machine);
    sceneRef.current={machine,bodies:[],arrows:[],pins:[],revision:0,camera,controls};
    const resize=()=>{const {width,height}=host.current.getBoundingClientRect();renderer.setSize(width,height);camera.aspect=width/height;camera.updateProjectionMatrix();};
    const observer=new ResizeObserver(resize);observer.observe(host.current);resize();
    let id;
    const animate=()=>{
      id=requestAnimationFrame(animate);
      const current=live.current, built=sceneRef.current;
      if(current && built.revision===current.revision){
        built.bodies.forEach((body,i)=>{
          const p=current.body_positions[i],q=current.body_quaternions[i];
          if(p && q){body.position.fromArray(p);body.quaternion.set(q[1],q[2],q[3],q[0]);}
        });
        built.arrows.forEach(({arrow,index})=>{
          const spin=current.metrics['rotor'+index+'_inertial_rpm']??0;
          const pitch=current.config.alternating && index%2 ? -1:1;
          arrow.visible=current.config.rotor_type==='propeller' && Math.abs(spin)>50;
          arrow.setDirection(new THREE.Vector3(0,0,-pitch*Math.sign(spin||1)));
        });
        if(current.config.mode==='free'){
          const target=new THREE.Vector3(...current.body_positions[1]);
          const delta=target.clone().sub(controls.target);
          camera.position.add(delta);controls.target.copy(target);
        }
        built.pins.forEach(({mesh,index})=>mesh.material.color.set(current.metrics['locked'+index]?'#ffca70':'#67e3c0'));
      }
      controls.update();renderer.render(scene,camera);
    };animate();
    return ()=>{cancelAnimationFrame(id);observer.disconnect();controls.dispose();
      scene.traverse(o=>{o.geometry?.dispose();if(o.material) o.material.dispose();});
      renderer.dispose();renderer.domElement.remove();sceneRef.current=null;};
  },[]);
  useEffect(()=>{
    const target=sceneRef.current;if(!target || !model)return;
    while(target.machine.children.length){
      const body=target.machine.children[0];
      body.traverse(o=>{o.geometry?.dispose();o.material?.dispose();});
      target.machine.remove(body);
    }
    target.camera.position.set(1.5,-1.9,2.15);target.controls.target.set(0,0,1.12);
    target.bodies=model.bodies.map(()=>{const g=new THREE.Group();target.machine.add(g);return g;});
    target.pins=[];target.arrows=[];
    const align=new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(1,0,0),Math.PI/2);
    model.geoms.forEach(g=>{
      let geometry;
      if(g.type===2)geometry=new THREE.SphereGeometry(g.size[0],20,12);
      else if(g.type===3){geometry=new THREE.CapsuleGeometry(g.size[0],2*g.size[1],4,12);geometry.applyQuaternion(align);}
      else if(g.type===5){geometry=new THREE.CylinderGeometry(g.size[0],g.size[0],2*g.size[1],40);geometry.applyQuaternion(align);}
      else if(g.type===6)geometry=new THREE.BoxGeometry(...g.size.map(v=>2*v));
      else return;
      const material=new THREE.MeshStandardMaterial({color:new THREE.Color(...g.color.slice(0,3)),metalness:.38,roughness:.35});
      const mesh=new THREE.Mesh(geometry,material);mesh.position.fromArray(g.pos);
      mesh.quaternion.set(g.quat[1],g.quat[2],g.quat[3],g.quat[0]);
      target.bodies[g.body].add(mesh);
      if(g.name.startsWith('pin_geom'))target.pins.push({mesh,index:Number(g.name.replace('pin_geom',''))});
    });
    model.bodies.forEach((name,i)=>{
      if(/^rotor[0-3]$/.test(name)){
        const arrow=new THREE.ArrowHelper(new THREE.Vector3(0,0,-1),new THREE.Vector3(.045,0,-.025),.17,0x57dfef,.04,.022);
        target.bodies[i].add(arrow);target.arrows.push({arrow,index:Number(name.slice(-1))});
      }
    });
    target.revision=model.revision;
  },[model]);
  return <div ref={host} className="scene-canvas" aria-label="Interactive 3D mechanical simulation"/>;
}
