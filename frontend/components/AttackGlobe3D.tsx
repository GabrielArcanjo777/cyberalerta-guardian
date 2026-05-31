"use client"

import React, {useEffect, useRef, useState} from 'react'
import * as THREE from 'three'

type ArcTone = 'threat' | 'protected' | 'monitoring'

type Region = {
  label:string
  lat:number
  lon:number
}

type Arc = {
  from:Region
  to:Region
  tone:ArcTone
}

type ArcVisual = {
  line:THREE.Line
  curve:THREE.QuadraticBezierCurve3
  pulse:THREE.Mesh
}

const colors:Record<ArcTone, number> = {
  threat: 0xef4444,
  protected: 0x22c55e,
  monitoring: 0x3b82f6,
}

const regions:Region[] = [
  {label:'Brazil protected hub', lat:-15.8, lon:-47.9},
  {label:'North America', lat:39, lon:-98},
  {label:'Western Europe', lat:50, lon:8},
  {label:'West Africa', lat:8, lon:2},
  {label:'India', lat:21, lon:78},
  {label:'Southeast Asia', lat:13, lon:101},
  {label:'Australia', lat:-25, lon:133},
  {label:'Middle East', lat:25, lon:45},
]

const hub = regions[0]

const arcs:Arc[] = [
  {from:regions[1], to:hub, tone:'threat'},
  {from:regions[2], to:hub, tone:'monitoring'},
  {from:regions[3], to:hub, tone:'protected'},
  {from:regions[4], to:hub, tone:'threat'},
  {from:regions[5], to:hub, tone:'monitoring'},
  {from:regions[6], to:hub, tone:'protected'},
  {from:regions[7], to:hub, tone:'threat'},
  {from:regions[2], to:regions[4], tone:'monitoring'},
  {from:regions[1], to:regions[5], tone:'threat'},
  {from:regions[3], to:regions[2], tone:'protected'},
  {from:regions[4], to:regions[7], tone:'monitoring'},
  {from:regions[6], to:regions[1], tone:'protected'},
]

function supportsWebGL(){
  try{
    const canvas = document.createElement('canvas')
    return Boolean(canvas.getContext('webgl') || canvas.getContext('experimental-webgl'))
  }catch{
    return false
  }
}

function latLonToVector3(lat:number, lon:number, radius:number){
  const phi = (90 - lat) * (Math.PI / 180)
  const theta = (lon + 180) * (Math.PI / 180)
  return new THREE.Vector3(
    -radius * Math.sin(phi) * Math.cos(theta),
    radius * Math.cos(phi),
    radius * Math.sin(phi) * Math.sin(theta)
  )
}

function makeCircleLine(radius:number, color:number, opacity:number){
  const points:THREE.Vector3[] = []
  for(let i = 0; i <= 128; i += 1){
    const angle = (i / 128) * Math.PI * 2
    points.push(new THREE.Vector3(Math.cos(angle) * radius, 0, Math.sin(angle) * radius))
  }
  return new THREE.Line(
    new THREE.BufferGeometry().setFromPoints(points),
    new THREE.LineBasicMaterial({color, transparent:true, opacity})
  )
}

function makeArcVisual(arc:Arc, radius:number):ArcVisual{
  const start = latLonToVector3(arc.from.lat, arc.from.lon, radius)
  const end = latLonToVector3(arc.to.lat, arc.to.lon, radius)
  const midpoint = start.clone().add(end).normalize().multiplyScalar(radius * 1.52)
  const curve = new THREE.QuadraticBezierCurve3(start, midpoint, end)
  const line = new THREE.Line(
    new THREE.BufferGeometry().setFromPoints(curve.getPoints(52)),
    new THREE.LineBasicMaterial({color:colors[arc.tone], transparent:true, opacity:0.78})
  )
  line.userData.tone = arc.tone
  const pulse = new THREE.Mesh(
    new THREE.SphereGeometry(0.032, 14, 14),
    new THREE.MeshBasicMaterial({color:colors[arc.tone], transparent:true, opacity:0.88})
  )
  pulse.userData.tone = arc.tone
  return {line, curve, pulse}
}

export default function AttackGlobe3D(){
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
    const camera = new THREE.PerspectiveCamera(38, 1, 0.1, 100)
    camera.position.set(0, 0.25, 6.6)

    const renderer = new THREE.WebGLRenderer({antialias:true, alpha:true, preserveDrawingBuffer:true})
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.8))
    renderer.setClearColor(0x000000, 0)
    renderer.outputColorSpace = THREE.SRGBColorSpace
    renderer.domElement.style.display = 'block'
    renderer.domElement.style.width = '100%'
    renderer.domElement.style.height = '100%'
    container.appendChild(renderer.domElement)

    const root = new THREE.Group()
    scene.add(root)
    const globeGroup = new THREE.Group()
    root.add(globeGroup)

    const globeRadius = 1.92
    const globe = new THREE.Mesh(
      new THREE.SphereGeometry(globeRadius, 64, 64),
      new THREE.MeshStandardMaterial({
        color:0x1e3a5f,
        emissive:0x10233b,
        roughness:0.58,
        metalness:0.08,
        transparent:true,
        opacity:0.84,
      })
    )
    globeGroup.add(globe)

    const atmosphere = new THREE.Mesh(
      new THREE.SphereGeometry(globeRadius * 1.045, 64, 64),
      new THREE.MeshBasicMaterial({
        color:0x38bdf8,
        transparent:true,
        opacity:0.08,
        side:THREE.BackSide,
      })
    )
    globeGroup.add(atmosphere)

    const gridLines:THREE.Line[] = []
    for(let lat = -60; lat <= 60; lat += 30){
      const y = globeRadius * Math.sin(lat * Math.PI / 180)
      const r = globeRadius * Math.cos(lat * Math.PI / 180)
      const line = makeCircleLine(r, 0x94a3b8, 0.28)
      line.position.y = y
      gridLines.push(line)
      globeGroup.add(line)
    }
    for(let lon = 0; lon < 180; lon += 30){
      const line = makeCircleLine(globeRadius, 0x94a3b8, 0.22)
      line.rotation.x = Math.PI / 2
      line.rotation.z = lon * Math.PI / 180
      gridLines.push(line)
      globeGroup.add(line)
    }

    const arcVisuals = arcs.map((arc)=>makeArcVisual(arc, globeRadius + 0.035))
    arcVisuals.forEach((visual,index)=>{
      visual.pulse.position.copy(visual.curve.getPoint((index * 0.086) % 1))
      globeGroup.add(visual.line)
      globeGroup.add(visual.pulse)
    })

    const nodeMeshes:THREE.Mesh[] = []
    regions.forEach((region, index)=>{
      const point = latLonToVector3(region.lat, region.lon, globeRadius + 0.07)
      const isHub = index === 0
      const node = new THREE.Mesh(
        new THREE.SphereGeometry(isHub ? 0.065 : 0.042, 18, 18),
        new THREE.MeshBasicMaterial({
          color:isHub ? 0x22c55e : 0x93c5fd,
          transparent:true,
          opacity:isHub ? 1 : 0.86,
        })
      )
      node.position.copy(point)
      node.userData.isHub = isHub
      nodeMeshes.push(node)
      globeGroup.add(node)
    })

    const starsGeometry = new THREE.BufferGeometry()
    const starPositions:number[] = []
    for(let i = 0; i < 140; i += 1){
      const radius = 3.2 + Math.random() * 1.8
      const theta = Math.random() * Math.PI * 2
      const phi = Math.acos((Math.random() * 2) - 1)
      starPositions.push(
        radius * Math.sin(phi) * Math.cos(theta),
        radius * Math.cos(phi),
        radius * Math.sin(phi) * Math.sin(theta)
      )
    }
    starsGeometry.setAttribute('position', new THREE.Float32BufferAttribute(starPositions, 3))
    const stars = new THREE.Points(
      starsGeometry,
      new THREE.PointsMaterial({color:0x94a3b8, size:0.018, transparent:true, opacity:0.32})
    )
    root.add(stars)

    scene.add(new THREE.AmbientLight(0xffffff, 0.36))
    const keyLight = new THREE.DirectionalLight(0xffffff, 1.1)
    keyLight.position.set(3.2, 2.8, 4.5)
    scene.add(keyLight)
    const blueLight = new THREE.PointLight(0x3b82f6, 1.1, 7)
    blueLight.position.set(-2.8, 1.4, 2.8)
    scene.add(blueLight)
    const greenLight = new THREE.PointLight(0x22c55e, 0.75, 6)
    greenLight.position.set(2.8, -1.2, 2.5)
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
        root.rotation.x += (((-pointer.y * 0.045) - root.rotation.x) * 0.035)
        root.rotation.y += (((pointer.x * 0.06) - root.rotation.y) * 0.035)
        globeGroup.rotation.y = elapsed * 0.115
        globeGroup.rotation.x = Math.sin(elapsed * 0.22) * 0.025
        stars.rotation.y = elapsed * 0.025
        atmosphere.scale.setScalar(1 + (Math.sin(elapsed * 0.8) + 1) * 0.01)
        arcVisuals.forEach((visual, index)=>{
          const material = visual.line.material as THREE.LineBasicMaterial
          material.opacity = 0.32 + (Math.sin(elapsed * 1.25 + index * 0.7) + 1) * 0.25
          const point = visual.curve.getPoint((elapsed * 0.135 + index * 0.086) % 1)
          visual.pulse.position.copy(point)
          const pulseMaterial = visual.pulse.material as THREE.MeshBasicMaterial
          pulseMaterial.opacity = 0.56 + (Math.sin(elapsed * 1.6 + index) + 1) * 0.16
        })
        nodeMeshes.forEach((node, index)=>{
          const pulse = 1 + (Math.sin(elapsed * 1.5 + index) + 1) * (node.userData.isHub ? 0.12 : 0.08)
          node.scale.setScalar(pulse)
        })
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
      globe.geometry.dispose()
      atmosphere.geometry.dispose()
      ;(atmosphere.material as THREE.Material).dispose()
      ;(globe.material as THREE.Material).dispose()
      gridLines.forEach(line=>{
        line.geometry.dispose()
        ;(line.material as THREE.Material).dispose()
      })
      arcVisuals.forEach(visual=>{
        visual.line.geometry.dispose()
        ;(visual.line.material as THREE.Material).dispose()
        visual.pulse.geometry.dispose()
        ;(visual.pulse.material as THREE.Material).dispose()
      })
      nodeMeshes.forEach(node=>{
        node.geometry.dispose()
        ;(node.material as THREE.Material).dispose()
      })
      starsGeometry.dispose()
      ;(stars.material as THREE.Material).dispose()
      renderer.dispose()
      renderer.domElement.remove()
    }
  },[])

  return (
    <section className="guardian-panel-dark overflow-hidden rounded-lg text-white">
      <div className="grid lg:grid-cols-[1.05fr_0.95fr]">
        <div className="relative min-h-[380px] sm:min-h-[500px]">
          {fallback ? (
            <div className="flex h-full min-h-[380px] items-center justify-center bg-slate-900 p-8 text-center">
              <div>
                <div className="text-xs font-bold uppercase text-blue-200">Radar global</div>
                <p className="mt-3 text-2xl font-black text-white">WebGL indisponivel</p>
                <p className="mt-3 text-sm font-semibold leading-6 text-slate-300">
                  A visualização simulada está resumida nos cards ao lado.
                </p>
              </div>
            </div>
          ) : (
            <>
              <div ref={mountRef} className="absolute inset-0" aria-hidden="true" />
              <div className="pointer-events-none absolute inset-0 bg-[linear-gradient(180deg,rgba(2,6,23,0.06),rgba(2,6,23,0.3)_76%,rgba(2,6,23,0.64))]" />
            </>
          )}
        </div>
        <div className="border-t border-white/10 p-6 sm:p-8 lg:border-l lg:border-t-0">
          <div className="text-xs font-bold uppercase text-blue-200">Radar global simulado</div>
          <h2 className="mt-4 text-3xl font-black text-white">
            Visibilidade global de pressões de fraude, vista pela camada Guardian.
          </h2>
          <p className="mt-4 text-sm font-semibold leading-6 text-slate-300">
            Visualização simulada — não é um feed real de ataques.
          </p>
          <div className="mt-6 grid gap-3">
            <LegendItem color="bg-red-500" label="Tentativas de risco" detail="Pressão por pagamento, credencial, identidade ou acesso remoto." />
            <LegendItem color="bg-emerald-500" label="Ações pausadas" detail="Trust Lock ou orientação do contato de confiança interrompeu o risco." />
            <LegendItem color="bg-blue-500" label="Monitoramento simulado" detail="Revisão defensiva sem alegar inteligência real ao vivo." />
          </div>
        </div>
      </div>
    </section>
  )
}

function LegendItem({color, label, detail}:{color:string, label:string, detail:string}){
  return (
    <div className="rounded-lg border border-white/10 bg-white/[0.04] p-4">
      <div className="flex items-center gap-3">
        <span className={`h-3 w-3 rounded-full ${color}`} />
        <span className="text-sm font-black text-white">{label}</span>
      </div>
      <p className="mt-2 text-sm leading-6 text-slate-300">{detail}</p>
    </div>
  )
}
