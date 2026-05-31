"use client"

import React, {useEffect, useRef, useState} from 'react'
import * as THREE from 'three'

function supportsWebGL(){
  try{
    const canvas = document.createElement('canvas')
    return Boolean(canvas.getContext('webgl') || canvas.getContext('experimental-webgl'))
  }catch{
    return false
  }
}

export default function Shield3DScene(){
  const mountRef = useRef<HTMLDivElement | null>(null)
  const [fallback,setFallback] = useState(false)

  useEffect(()=>{
    const mount = mountRef.current
    if(!mount || !supportsWebGL()){
      setFallback(true)
      return
    }
    const container = mount

    const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches
    const scene = new THREE.Scene()
    const camera = new THREE.PerspectiveCamera(36, 1, 0.1, 100)
    camera.position.set(0, 0.4, 6.2)

    const renderer = new THREE.WebGLRenderer({antialias:true, alpha:true, preserveDrawingBuffer:true})
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.8))
    renderer.setClearColor(0x000000, 0)
    renderer.outputColorSpace = THREE.SRGBColorSpace
    renderer.domElement.style.display = 'block'
    renderer.domElement.style.width = '100%'
    renderer.domElement.style.height = '100%'
    container.appendChild(renderer.domElement)

    const group = new THREE.Group()
    scene.add(group)

    const shieldShape = new THREE.Shape()
    shieldShape.moveTo(0, 1.62)
    shieldShape.bezierCurveTo(0.94, 1.42, 1.38, 1.12, 1.44, 0.7)
    shieldShape.bezierCurveTo(1.3, -0.68, 0.58, -1.42, 0, -1.78)
    shieldShape.bezierCurveTo(-0.58, -1.42, -1.3, -0.68, -1.44, 0.7)
    shieldShape.bezierCurveTo(-1.38, 1.12, -0.94, 1.42, 0, 1.62)

    const shieldGeometry = new THREE.ExtrudeGeometry(shieldShape, {
      depth: 0.22,
      bevelEnabled: true,
      bevelThickness: 0.045,
      bevelSize: 0.045,
      bevelSegments: 4,
    })
    shieldGeometry.center()

    const shield = new THREE.Mesh(
      shieldGeometry,
      new THREE.MeshStandardMaterial({
        color: 0x1d4ed8,
        emissive: 0x0f2a44,
        roughness: 0.35,
        metalness: 0.34,
      })
    )
    shield.rotation.x = -0.08
    group.add(shield)

    const edges = new THREE.LineSegments(
      new THREE.EdgesGeometry(shieldGeometry),
      new THREE.LineBasicMaterial({color: 0x7dd3fc, transparent:true, opacity:0.52})
    )
    edges.rotation.copy(shield.rotation)
    group.add(edges)

    const core = new THREE.Mesh(
      new THREE.TorusGeometry(0.78, 0.018, 12, 96),
      new THREE.MeshBasicMaterial({color:0x22c55e, transparent:true, opacity:0.82})
    )
    core.position.z = 0.2
    group.add(core)

    const innerCore = new THREE.Mesh(
      new THREE.IcosahedronGeometry(0.42, 1),
      new THREE.MeshStandardMaterial({color:0x0f172a, emissive:0x123f37, roughness:0.34, metalness:0.2})
    )
    innerCore.position.z = 0.23
    group.add(innerCore)

    const halo = new THREE.Mesh(
      new THREE.TorusGeometry(1.68, 0.012, 12, 128),
      new THREE.MeshBasicMaterial({color:0x3b82f6, transparent:true, opacity:0.28})
    )
    halo.rotation.x = Math.PI / 2.45
    group.add(halo)

    const orbitRing = new THREE.Mesh(
      new THREE.TorusGeometry(2.04, 0.01, 12, 160),
      new THREE.MeshBasicMaterial({color:0x7dd3fc, transparent:true, opacity:0.18})
    )
    orbitRing.rotation.x = Math.PI / 2.9
    orbitRing.rotation.y = 0.42
    group.add(orbitRing)

    const trustRing = new THREE.Mesh(
      new THREE.TorusGeometry(1.18, 0.01, 12, 128),
      new THREE.MeshBasicMaterial({color:0x22c55e, transparent:true, opacity:0.28})
    )
    trustRing.rotation.x = Math.PI / 2.2
    trustRing.rotation.y = -0.35
    group.add(trustRing)

    const pointsGeometry = new THREE.BufferGeometry()
    const pointPositions:number[] = []
    for(let i = 0; i < 80; i += 1){
      const radius = 2.15 + Math.random() * 0.6
      const angle = Math.random() * Math.PI * 2
      const height = (Math.random() - 0.5) * 2.8
      pointPositions.push(Math.cos(angle) * radius, height, Math.sin(angle) * radius)
    }
    pointsGeometry.setAttribute('position', new THREE.Float32BufferAttribute(pointPositions, 3))
    const points = new THREE.Points(
      pointsGeometry,
      new THREE.PointsMaterial({color:0x94a3b8, size:0.025, transparent:true, opacity:0.48})
    )
    group.add(points)

    scene.add(new THREE.AmbientLight(0xffffff, 0.42))
    const keyLight = new THREE.DirectionalLight(0xffffff, 1.3)
    keyLight.position.set(3, 3, 4)
    scene.add(keyLight)
    const cyanLight = new THREE.PointLight(0x38bdf8, 1.25, 7)
    cyanLight.position.set(-2.4, 1.2, 2.4)
    scene.add(cyanLight)
    const greenLight = new THREE.PointLight(0x22c55e, 0.9, 6)
    greenLight.position.set(2.4, -1.6, 2.2)
    scene.add(greenLight)

    let frameId = 0
    let disposed = false
    const startedAt = performance.now()
    const pointer = {x:0, y:0}

    function onPointerMove(event:PointerEvent){
      const rect = container.getBoundingClientRect()
      pointer.x = ((event.clientX - rect.left) / Math.max(1, rect.width) - 0.5) * 2
      pointer.y = ((event.clientY - rect.top) / Math.max(1, rect.height) - 0.5) * 2
    }

    function resize(){
      const {width, height} = container.getBoundingClientRect()
      const safeWidth = Math.max(1, width)
      const safeHeight = Math.max(1, height)
      renderer.setSize(safeWidth, safeHeight, false)
      camera.aspect = safeWidth / safeHeight
      camera.updateProjectionMatrix()
    }

    function animate(){
      if(disposed) return
      const elapsed = (performance.now() - startedAt) / 1000
      if(!reducedMotion){
        group.rotation.y = elapsed * 0.18 + pointer.x * 0.07
        group.rotation.x = Math.sin(elapsed * 0.45) * 0.055 - pointer.y * 0.04
        group.position.y = Math.sin(elapsed * 0.55) * 0.055
        core.rotation.z = elapsed * 0.45
        halo.rotation.z = elapsed * 0.16
        orbitRing.rotation.z = -elapsed * 0.11
        trustRing.rotation.z = elapsed * 0.24
        innerCore.rotation.y = elapsed * 0.5
        points.rotation.y = -elapsed * 0.045
        ;(points.material as THREE.PointsMaterial).opacity = 0.36 + (Math.sin(elapsed * 0.8) + 1) * 0.08
      }
      renderer.render(scene, camera)
      frameId = window.requestAnimationFrame(animate)
    }

    resize()
    animate()
    window.addEventListener('resize', resize)
    container.addEventListener('pointermove', onPointerMove)

    return ()=>{
      disposed = true
      window.cancelAnimationFrame(frameId)
      window.removeEventListener('resize', resize)
      container.removeEventListener('pointermove', onPointerMove)
      shieldGeometry.dispose()
      edges.geometry.dispose()
      core.geometry.dispose()
      innerCore.geometry.dispose()
      halo.geometry.dispose()
      orbitRing.geometry.dispose()
      trustRing.geometry.dispose()
      pointsGeometry.dispose()
      ;[shield.material, edges.material, core.material, innerCore.material, halo.material, orbitRing.material, trustRing.material, points.material].forEach((material)=>{
        if(Array.isArray(material)){
          material.forEach(item=>item.dispose())
        }else{
          material.dispose()
        }
      })
      renderer.dispose()
      renderer.domElement.remove()
    }
  },[])

  if(fallback){
    return (
      <div className="flex h-full min-h-[320px] items-center justify-center rounded-lg border border-white/10 bg-slate-900 text-center">
        <div>
          <div className="mx-auto flex h-24 w-20 items-center justify-center rounded-md border border-cyan-300/40 bg-slate-800 text-3xl font-black text-cyan-200">
            G
          </div>
          <p className="mt-4 text-sm font-semibold text-slate-300">Identidade de proteção Guardian</p>
        </div>
      </div>
    )
  }

  return (
    <div className="guardian-panel-dark relative min-h-[360px] overflow-hidden rounded-lg" aria-label="Guardian defensive shield visualization">
      <div ref={mountRef} className="absolute inset-0" aria-hidden="true" />
      <div className="pointer-events-none absolute inset-0 bg-[linear-gradient(180deg,transparent_0%,rgba(2,6,23,0.36)_74%,rgba(2,6,23,0.72)_100%)]" />
      <div className="pointer-events-none absolute inset-x-4 bottom-4 rounded-lg border border-white/10 bg-slate-950/72 p-4 backdrop-blur">
        <div className="text-xs font-bold uppercase text-cyan-200">Núcleo Guardian</div>
        <p className="mt-2 text-sm font-semibold leading-6 text-slate-200">
          Identidade protetiva, revisão de confiança e pausa antes do dano.
        </p>
      </div>
    </div>
  )
}
