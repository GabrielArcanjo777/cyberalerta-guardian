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

function makeRing(radius:number, color:number, opacity:number){
  return new THREE.Mesh(
    new THREE.TorusGeometry(radius, 0.008, 8, 112),
    new THREE.MeshBasicMaterial({color, transparent:true, opacity})
  )
}

export default function HomeGuardianCoreVisual(){
  const mountRef = useRef<HTMLDivElement | null>(null)
  const [fallback,setFallback]=useState(false)

  useEffect(()=>{
    const mount = mountRef.current
    if(!mount || !supportsWebGL()){
      setFallback(true)
      return
    }

    const container = mount
    const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches
    const motionScale = reducedMotion ? 0.12 : 1
    const scene = new THREE.Scene()
    const camera = new THREE.PerspectiveCamera(34, 1, 0.1, 100)
    camera.position.set(0, 0.12, 6.3)

    const renderer = new THREE.WebGLRenderer({antialias:true, alpha:true, powerPreference:'high-performance'})
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.5))
    renderer.setClearColor(0x000000, 0)
    renderer.outputColorSpace = THREE.SRGBColorSpace
    renderer.domElement.style.display = 'block'
    renderer.domElement.style.width = '100%'
    renderer.domElement.style.height = '100%'
    renderer.domElement.style.pointerEvents = 'none'
    container.appendChild(renderer.domElement)

    const root = new THREE.Group()
    const coreGroup = new THREE.Group()
    scene.add(root)
    root.add(coreGroup)

    const coreGeometry = new THREE.IcosahedronGeometry(0.86, 2)
    const coreMaterial = new THREE.MeshStandardMaterial({
      color:0x101419,
      emissive:0x061015,
      roughness:0.34,
      metalness:0.72,
    })
    const core = new THREE.Mesh(coreGeometry, coreMaterial)
    coreGroup.add(core)

    const wire = new THREE.LineSegments(
      new THREE.EdgesGeometry(coreGeometry),
      new THREE.LineBasicMaterial({color:0xb6c2cf, transparent:true, opacity:0.22})
    )
    coreGroup.add(wire)

    const innerGeometry = new THREE.OctahedronGeometry(0.44, 1)
    const innerMaterial = new THREE.MeshStandardMaterial({
      color:0x071013,
      emissive:0x063233,
      roughness:0.42,
      metalness:0.4,
    })
    const inner = new THREE.Mesh(innerGeometry, innerMaterial)
    coreGroup.add(inner)

    const rings = [
      makeRing(1.28, 0x93a4b8, 0.18),
      makeRing(1.62, 0x22d3ee, 0.14),
      makeRing(2.02, 0x94a3b8, 0.1),
    ]
    rings[0].rotation.x = Math.PI / 2.6
    rings[1].rotation.x = Math.PI / 2.1
    rings[1].rotation.y = -0.46
    rings[2].rotation.x = Math.PI / 2.85
    rings[2].rotation.y = 0.44
    rings.forEach(ring=>coreGroup.add(ring))

    const nodeGeometry = new THREE.SphereGeometry(0.034, 10, 10)
    const nodeMaterial = new THREE.MeshBasicMaterial({color:0xb8c7d9, transparent:true, opacity:0.72})
    const safeNodeMaterial = new THREE.MeshBasicMaterial({color:0x34d399, transparent:true, opacity:0.72})
    const riskNodeMaterial = new THREE.MeshBasicMaterial({color:0xf87171, transparent:true, opacity:0.68})
    const nodePositions = [
      [-1.55, 0.55, 0.42],
      [-1.08, -0.62, -0.36],
      [-0.18, 1.35, 0.1],
      [1.3, 0.7, -0.28],
      [1.58, -0.34, 0.3],
      [0.48, -1.24, -0.2],
      [0.18, 0.18, 1.62],
      [-0.62, 0.18, -1.42],
    ]
    const nodes = nodePositions.map((position,index)=>{
      const material = index === 4 ? riskNodeMaterial : index === 6 ? safeNodeMaterial : nodeMaterial
      const node = new THREE.Mesh(nodeGeometry, material)
      node.position.set(position[0], position[1], position[2])
      node.userData.index = index
      coreGroup.add(node)
      return node
    })

    const linePositions:number[] = []
    nodes.forEach((node,index)=>{
      const next = nodes[(index + 2) % nodes.length]
      linePositions.push(node.position.x, node.position.y, node.position.z)
      linePositions.push(next.position.x, next.position.y, next.position.z)
    })
    const meshGeometry = new THREE.BufferGeometry()
    meshGeometry.setAttribute('position', new THREE.Float32BufferAttribute(linePositions, 3))
    const meshLines = new THREE.LineSegments(
      meshGeometry,
      new THREE.LineBasicMaterial({color:0x7890a8, transparent:true, opacity:0.16})
    )
    coreGroup.add(meshLines)

    const pulseRing = makeRing(1.06, 0xf87171, 0.12)
    pulseRing.rotation.x = Math.PI / 2.18
    pulseRing.rotation.y = 0.3
    coreGroup.add(pulseRing)

    const fieldGeometry = new THREE.BufferGeometry()
    const fieldPositions:number[] = []
    for(let i = 0; i < 70; i += 1){
      const radius = 2.25 + Math.random() * 0.95
      const angle = Math.random() * Math.PI * 2
      const z = (Math.random() - 0.5) * 2.4
      fieldPositions.push(Math.cos(angle) * radius, Math.sin(angle) * radius * 0.58, z)
    }
    fieldGeometry.setAttribute('position', new THREE.Float32BufferAttribute(fieldPositions, 3))
    const field = new THREE.Points(
      fieldGeometry,
      new THREE.PointsMaterial({color:0x94a3b8, size:0.018, transparent:true, opacity:0.34})
    )
    root.add(field)

    scene.add(new THREE.AmbientLight(0xffffff, 0.34))
    const key = new THREE.DirectionalLight(0xffffff, 1.12)
    key.position.set(2.4, 2.8, 4)
    scene.add(key)
    const cyan = new THREE.PointLight(0x22d3ee, 0.72, 7)
    cyan.position.set(-2.4, 1.4, 2.6)
    scene.add(cyan)
    const warm = new THREE.PointLight(0x64748b, 0.68, 6)
    warm.position.set(2.6, -1.5, 2.2)
    scene.add(warm)

    let disposed = false
    let frameId = 0
    const startedAt = performance.now()

    function resize(){
      const {width,height} = container.getBoundingClientRect()
      const safeWidth = Math.max(1, width)
      const safeHeight = Math.max(1, height)
      renderer.setSize(safeWidth, safeHeight, false)
      camera.aspect = safeWidth / safeHeight
      camera.updateProjectionMatrix()
    }

    function animate(){
      if(disposed) return
      const elapsed = ((performance.now() - startedAt) / 1000) * motionScale
      root.rotation.y = elapsed * 0.12
      coreGroup.rotation.y = elapsed * 0.42
      coreGroup.rotation.x = Math.sin(elapsed * 0.54) * 0.08
      core.rotation.y = -elapsed * 0.2
      inner.rotation.x = elapsed * 0.56
      inner.rotation.y = -elapsed * 0.48
      rings[0].rotation.z = elapsed * 0.22
      rings[1].rotation.z = -elapsed * 0.18
      rings[2].rotation.z = elapsed * 0.12
      field.rotation.z = -elapsed * 0.04
      const pulse = 0.5 + (Math.sin(elapsed * 1.7) + 1) * 0.5
      pulseRing.scale.setScalar(1 + pulse * 0.08)
      ;(pulseRing.material as THREE.MeshBasicMaterial).opacity = 0.06 + pulse * 0.16
      ;(meshLines.material as THREE.LineBasicMaterial).opacity = 0.1 + pulse * 0.08
      nodes.forEach((node,index)=>{
        const localPulse = 0.94 + Math.sin(elapsed * 1.2 + index) * 0.08
        node.scale.setScalar(localPulse)
      })
      renderer.render(scene, camera)
      frameId = window.requestAnimationFrame(animate)
    }

    resize()
    animate()
    window.addEventListener('resize', resize)

    return ()=>{
      disposed = true
      window.cancelAnimationFrame(frameId)
      window.removeEventListener('resize', resize)
      coreGeometry.dispose()
      wire.geometry.dispose()
      innerGeometry.dispose()
      rings.forEach(ring=>ring.geometry.dispose())
      nodeGeometry.dispose()
      meshGeometry.dispose()
      pulseRing.geometry.dispose()
      fieldGeometry.dispose()
      ;[
        coreMaterial,
        wire.material,
        innerMaterial,
        ...rings.map(ring=>ring.material),
        nodeMaterial,
        safeNodeMaterial,
        riskNodeMaterial,
        meshLines.material,
        pulseRing.material,
        field.material,
      ].forEach(material=>{
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
      <div className="home-core-visual home-core-fallback">
        <div className="home-core-fallback-mark">CG</div>
        <p>Defense Mesh Core</p>
      </div>
    )
  }

  return (
    <div className="home-core-visual" aria-label="Núcleo visual de proteção assistida">
      <div className="home-core-orbit home-core-orbit-a" />
      <div className="home-core-orbit home-core-orbit-b" />
      <div ref={mountRef} className="pointer-events-none absolute inset-0 z-[2]" aria-hidden="true" />
      <div className="home-core-caption">
        <span>Defense Mesh Core</span>
        <strong>Proteção assistida em tempo de decisão</strong>
      </div>
    </div>
  )
}
