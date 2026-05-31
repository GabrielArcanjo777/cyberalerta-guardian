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
    const motionScale = reducedMotion ? 0.18 : 1
    const scene = new THREE.Scene()
    const camera = new THREE.PerspectiveCamera(36, 1, 0.1, 100)
    camera.position.set(0, 0.4, 6.2)

    const renderer = new THREE.WebGLRenderer({antialias:true, alpha:true, powerPreference:'high-performance'})
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.5))
    renderer.setClearColor(0x000000, 0)
    renderer.outputColorSpace = THREE.SRGBColorSpace
    renderer.domElement.style.display = 'block'
    renderer.domElement.style.width = '100%'
    renderer.domElement.style.height = '100%'
    renderer.domElement.style.pointerEvents = 'none'
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
      bevelSegments: 2,
    })
    shieldGeometry.center()

    const shieldMaterial = new THREE.MeshStandardMaterial({
        color: 0x1d4ed8,
        emissive: 0x0f2a44,
        roughness: 0.35,
        metalness: 0.34,
      })
    const shield = new THREE.Mesh(shieldGeometry, shieldMaterial)
    shield.rotation.x = -0.08
    group.add(shield)

    const edgeMaterial = new THREE.LineBasicMaterial({color: 0x7dd3fc, transparent:true, opacity:0.62})
    const edges = new THREE.LineSegments(
      new THREE.EdgesGeometry(shieldGeometry),
      edgeMaterial
    )
    edges.rotation.copy(shield.rotation)
    group.add(edges)

    const coreMaterial = new THREE.MeshBasicMaterial({color:0x22c55e, transparent:true, opacity:0.9})
    const core = new THREE.Mesh(
      new THREE.TorusGeometry(0.78, 0.018, 10, 72),
      coreMaterial
    )
    core.position.z = 0.2
    group.add(core)

    const innerCore = new THREE.Mesh(
      new THREE.IcosahedronGeometry(0.42, 1),
      new THREE.MeshStandardMaterial({color:0x0f172a, emissive:0x123f37, roughness:0.34, metalness:0.2})
    )
    innerCore.position.z = 0.23
    group.add(innerCore)

    const haloMaterial = new THREE.MeshBasicMaterial({color:0x3b82f6, transparent:true, opacity:0.34})
    const halo = new THREE.Mesh(
      new THREE.TorusGeometry(1.68, 0.012, 10, 96),
      haloMaterial
    )
    halo.rotation.x = Math.PI / 2.45
    group.add(halo)

    const orbitMaterial = new THREE.MeshBasicMaterial({color:0x7dd3fc, transparent:true, opacity:0.24})
    const orbitRing = new THREE.Mesh(
      new THREE.TorusGeometry(2.04, 0.01, 10, 112),
      orbitMaterial
    )
    orbitRing.rotation.x = Math.PI / 2.9
    orbitRing.rotation.y = 0.42
    group.add(orbitRing)

    const trustMaterial = new THREE.MeshBasicMaterial({color:0x22c55e, transparent:true, opacity:0.34})
    const trustRing = new THREE.Mesh(
      new THREE.TorusGeometry(1.18, 0.01, 10, 88),
      trustMaterial
    )
    trustRing.rotation.x = Math.PI / 2.2
    trustRing.rotation.y = -0.35
    group.add(trustRing)

    const pointsGeometry = new THREE.BufferGeometry()
    const pointPositions:number[] = []
    for(let i = 0; i < 52; i += 1){
      const radius = 2.15 + Math.random() * 0.6
      const angle = Math.random() * Math.PI * 2
      const height = (Math.random() - 0.5) * 2.8
      pointPositions.push(Math.cos(angle) * radius, height, Math.sin(angle) * radius)
    }
    pointsGeometry.setAttribute('position', new THREE.Float32BufferAttribute(pointPositions, 3))
    const points = new THREE.Points(
      pointsGeometry,
      new THREE.PointsMaterial({color:0x94a3b8, size:0.026, transparent:true, opacity:0.42})
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
      const activeTime = elapsed * motionScale
      group.rotation.y = activeTime * 0.34 + pointer.x * 0.08
      group.rotation.x = Math.sin(activeTime * 0.72) * 0.075 - pointer.y * 0.045
      group.position.y = Math.sin(activeTime * 0.75) * 0.075
      shield.rotation.y = Math.sin(activeTime * 0.7) * 0.06
      shield.scale.setScalar(1 + Math.sin(activeTime * 1.1) * 0.012)
      edges.rotation.copy(shield.rotation)
      edges.scale.copy(shield.scale)
      core.rotation.z = activeTime * 0.82
      core.scale.setScalar(1 + (Math.sin(activeTime * 1.35) + 1) * 0.018)
      halo.rotation.z = activeTime * 0.3
      orbitRing.rotation.z = -activeTime * 0.22
      trustRing.rotation.z = activeTime * 0.42
      innerCore.rotation.y = activeTime * 0.88
      innerCore.rotation.x = Math.sin(activeTime * 0.65) * 0.12
      points.rotation.y = -activeTime * 0.09
      edgeMaterial.opacity = 0.46 + (Math.sin(activeTime * 1.05) + 1) * 0.11
      coreMaterial.opacity = 0.68 + (Math.sin(activeTime * 1.24) + 1) * 0.14
      haloMaterial.opacity = 0.2 + (Math.sin(activeTime * 0.88) + 1) * 0.12
      orbitMaterial.opacity = 0.14 + (Math.sin(activeTime * 0.74 + 1) + 1) * 0.08
      trustMaterial.opacity = 0.22 + (Math.sin(activeTime * 1.05 + 2) + 1) * 0.09
      ;(points.material as THREE.PointsMaterial).opacity = 0.36 + (Math.sin(activeTime * 1.05) + 1) * 0.11
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
    <div className="guardian-shield-stage relative min-h-[360px] overflow-hidden rounded-lg" aria-label="Guardian defensive shield visualization">
      <div ref={mountRef} className="pointer-events-none absolute inset-0 z-[1]" aria-hidden="true" />
      <div className="pointer-events-none absolute inset-0 z-[2] bg-[radial-gradient(circle_at_52%_36%,rgba(56,189,248,0.13),transparent_32%),linear-gradient(180deg,transparent_0%,rgba(2,6,23,0.2)_74%,rgba(2,6,23,0.58)_100%)]" />
      <div className="pointer-events-none absolute inset-x-4 bottom-4 z-[3] rounded-md border border-cyan-300/15 bg-slate-950/76 p-4 shadow-[0_18px_44px_rgba(2,6,23,0.35)] backdrop-blur">
        <div className="text-[11px] font-bold uppercase tracking-[0.18em] text-cyan-200">Guardian core</div>
        <p className="mt-2 text-sm font-medium leading-6 text-slate-200">
          Camada defensiva para pausar, explicar e encaminhar risco antes do dano.
        </p>
      </div>
    </div>
  )
}
