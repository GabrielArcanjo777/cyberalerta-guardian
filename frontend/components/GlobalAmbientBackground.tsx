"use client"

import React, {useEffect, useRef} from 'react'
import {usePathname} from 'next/navigation'

type Particle = {
  x:number
  y:number
  vx:number
  vy:number
  depth:number
  phase:number
  radius:number
}

type Cluster = {
  x:number
  y:number
  radius:number
  phase:number
  nodes:Array<{x:number,y:number,size:number,delay:number}>
}

type Route = {
  points:Array<{x:number,y:number}>
  phase:number
  tone:'cyan'|'green'|'slate'
}

const frameInterval = 1000 / 30

export default function GlobalAmbientBackground(){
  const canvasRef = useRef<HTMLCanvasElement | null>(null)
  const pathname = usePathname()
  const disabledOnHome = pathname === '/'
  const animatedOnGlobal = pathname === '/global'

  useEffect(()=>{
    if(disabledOnHome || !animatedOnGlobal) return

    const canvas = canvasRef.current
    if(!canvas) return

    const activeCanvas = canvas
    const context = activeCanvas.getContext('2d')
    if(!context) return
    const ctx = context

    const media = window.matchMedia('(prefers-reduced-motion: reduce)')
    const reducedMotion = media.matches
    const compactMotion = window.matchMedia('(max-width: 768px)').matches
    const motionScale = reducedMotion ? 0.16 : compactMotion ? 0.48 : 0.82
    const particles:Particle[] = []
    const clusters:Cluster[] = []
    const routes:Route[] = []
    let width = 0
    let height = 0
    let dpr = 1
    let frameId = 0
    let disposed = false
    let lastDraw = 0

    function createParticles(){
      particles.length = 0
      const baseCount = compactMotion ? 28 : 52
      const count = Math.min(compactMotion ? 42 : 78, Math.max(baseCount, Math.floor((width * height) / 26000)))
      for(let i = 0; i < count; i += 1){
        const depth = 0.35 + Math.random() * 0.65
        particles.push({
          x: Math.random() * width,
          y: Math.random() * height,
          vx: (Math.random() - 0.5) * 0.48 * depth,
          vy: (Math.random() - 0.5) * 0.36 * depth,
          depth,
          phase: Math.random() * Math.PI * 2,
          radius: 0.9 + Math.random() * 1.9,
        })
      }
    }

    function createClusters(){
      clusters.length = 0
      routes.length = 0

      const clusterSeeds = compactMotion
        ? [
            [0.22, 0.24, 52, 0],
            [0.78, 0.34, 58, 1.2],
            [0.58, 0.76, 48, 2.4],
          ]
        : [
            [0.16, 0.2, 78, 0],
            [0.42, 0.34, 64, 0.9],
            [0.78, 0.28, 88, 1.8],
            [0.22, 0.74, 68, 2.7],
            [0.68, 0.78, 76, 3.5],
          ]

      clusterSeeds.forEach(([px, py, radius, phase])=>{
        const nodes = Array.from({length: compactMotion ? 5 : 8}, (_,index)=> {
          const angle = (Math.PI * 2 * index) / (compactMotion ? 5 : 8) + phase
          const distance = radius * (0.22 + ((index % 3) * 0.16))
          return {
            x: Math.cos(angle) * distance,
            y: Math.sin(angle) * distance * 0.72,
            size: 1.2 + (index % 3) * 0.45,
            delay: index * 0.4,
          }
        })
        clusters.push({
          x: width * px,
          y: height * py,
          radius,
          phase,
          nodes,
        })
      })

      const routeSeeds = compactMotion
        ? [
            [[0.04,0.28],[0.32,0.36],[0.58,0.52],[0.96,0.48]],
            [[0.08,0.72],[0.38,0.62],[0.72,0.7],[0.94,0.82]],
          ]
        : [
            [[0.02,0.24],[0.22,0.28],[0.44,0.18],[0.72,0.3],[0.98,0.22]],
            [[0.05,0.66],[0.25,0.58],[0.46,0.64],[0.75,0.54],[0.98,0.62]],
            [[0.12,0.88],[0.34,0.78],[0.62,0.86],[0.86,0.72],[1.02,0.78]],
            [[-0.02,0.44],[0.18,0.5],[0.38,0.42],[0.66,0.48],[0.94,0.38]],
          ]

      routeSeeds.forEach((route,index)=> {
        routes.push({
          points: route.map(([px,py])=>({x:width * px, y:height * py})),
          phase: index * 120,
          tone: index % 3 === 0 ? 'cyan' : index % 3 === 1 ? 'green' : 'slate',
        })
      })
    }

    function resize(){
      const rect = activeCanvas.getBoundingClientRect()
      width = Math.max(1, rect.width)
      height = Math.max(1, rect.height)
      dpr = Math.min(window.devicePixelRatio || 1, 1.5)
      activeCanvas.width = Math.floor(width * dpr)
      activeCanvas.height = Math.floor(height * dpr)
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0)
      createParticles()
      createClusters()
    }

    function drawRoute(route:Route, time:number){
      const color = route.tone === 'green' ? '52, 211, 153' : route.tone === 'cyan' ? '56, 189, 248' : '148, 163, 184'
      ctx.save()
      ctx.lineWidth = 1
      ctx.strokeStyle = `rgba(${color}, ${compactMotion ? 0.08 : 0.105})`
      ctx.beginPath()
      route.points.forEach((point,index)=> {
        if(index === 0){
          ctx.moveTo(point.x, point.y)
          return
        }
        const previous = route.points[index - 1]
        const cx = (previous.x + point.x) / 2
        ctx.quadraticCurveTo(cx, previous.y + Math.sin(index + route.phase) * 18, point.x, point.y)
      })
      ctx.stroke()

      if(!reducedMotion){
        ctx.setLineDash([42, 160])
        ctx.lineDashOffset = -((time * 0.035 * motionScale + route.phase) % 202)
        ctx.strokeStyle = `rgba(${color}, ${compactMotion ? 0.22 : 0.3})`
        ctx.beginPath()
        route.points.forEach((point,index)=> {
          if(index === 0){
            ctx.moveTo(point.x, point.y)
            return
          }
          const previous = route.points[index - 1]
          const cx = (previous.x + point.x) / 2
          ctx.quadraticCurveTo(cx, previous.y + Math.sin(index + route.phase) * 18, point.x, point.y)
        })
        ctx.stroke()
      }
      ctx.restore()
    }

    function draw(time:number){
      if(time - lastDraw < (reducedMotion ? frameInterval * 2 : frameInterval)){
        if(!disposed){
          frameId = window.requestAnimationFrame(draw)
        }
        return
      }
      lastDraw = time
      ctx.clearRect(0, 0, width, height)

      const animatedTime = time * motionScale
      const sweep = ((animatedTime * 0.032) % (width + 420)) - 210
      const secondarySweep = width - ((animatedTime * 0.022) % (width + 520))
      const glowA = ctx.createRadialGradient(width * 0.2, height * 0.18, 0, width * 0.2, height * 0.18, Math.max(width, height) * 0.46)
      glowA.addColorStop(0, 'rgba(56, 189, 248, 0.11)')
      glowA.addColorStop(0.44, 'rgba(56, 189, 248, 0.035)')
      glowA.addColorStop(1, 'rgba(56, 189, 248, 0)')
      ctx.fillStyle = glowA
      ctx.fillRect(0, 0, width, height)

      const glowB = ctx.createRadialGradient(width * 0.82, height * 0.46, 0, width * 0.82, height * 0.46, Math.max(width, height) * 0.54)
      glowB.addColorStop(0, 'rgba(20, 184, 166, 0.075)')
      glowB.addColorStop(0.4, 'rgba(20, 184, 166, 0.026)')
      glowB.addColorStop(1, 'rgba(34, 197, 94, 0)')
      ctx.fillStyle = glowB
      ctx.fillRect(0, 0, width, height)

      ctx.save()
      ctx.lineWidth = 1
      ctx.strokeStyle = 'rgba(148, 163, 184, 0.045)'
      const major = compactMotion ? 128 : 104
      const minor = major / 4
      for(let x = (animatedTime * 0.003) % minor; x < width; x += minor){
        ctx.globalAlpha = x % major < 2 ? 0.9 : 0.42
        ctx.beginPath()
        ctx.moveTo(x, 0)
        ctx.lineTo(x, height)
        ctx.stroke()
      }
      for(let y = (animatedTime * 0.002) % minor; y < height; y += minor){
        ctx.globalAlpha = y % major < 2 ? 0.72 : 0.34
        ctx.beginPath()
        ctx.moveTo(0, y)
        ctx.lineTo(width, y)
        ctx.stroke()
      }
      ctx.restore()

      routes.forEach((route)=>drawRoute(route, animatedTime))

      ctx.save()
      ctx.lineWidth = 1
      ctx.strokeStyle = 'rgba(125, 211, 252, 0.1)'
      for(let i = 0; i < (compactMotion ? 2 : 4); i += 1){
        const offset = i * 120
        ctx.beginPath()
        ctx.moveTo(sweep - offset, 0)
        ctx.lineTo(sweep + 140 - offset, height)
        ctx.stroke()
      }

      ctx.strokeStyle = 'rgba(52, 211, 153, 0.06)'
      for(let i = 0; i < (compactMotion ? 1 : 2); i += 1){
        const offset = i * 160
        ctx.beginPath()
        ctx.moveTo(secondarySweep + offset, 0)
        ctx.lineTo(secondarySweep - 160 + offset, height)
        ctx.stroke()
      }
      ctx.restore()

      ctx.save()
      clusters.forEach((cluster,index)=>{
        const pulse = 0.5 + (Math.sin(animatedTime * 0.002 + cluster.phase) + 1) * 0.5
        ctx.strokeStyle = `rgba(56, 189, 248, ${0.045 + pulse * 0.04})`
        ctx.lineWidth = 1
        ctx.beginPath()
        ctx.ellipse(cluster.x, cluster.y, cluster.radius, cluster.radius * 0.58, 0, 0, Math.PI * 2)
        ctx.stroke()

        if(!compactMotion){
          ctx.strokeStyle = `rgba(148, 163, 184, ${0.035 + pulse * 0.03})`
          ctx.beginPath()
          ctx.ellipse(cluster.x, cluster.y, cluster.radius * 1.42, cluster.radius * 0.86, 0, 0, Math.PI * 2)
          ctx.stroke()
        }

        cluster.nodes.forEach((node)=>{
          const nx = cluster.x + node.x
          const ny = cluster.y + node.y
          const nodePulse = 0.55 + (Math.sin(animatedTime * 0.004 + node.delay + cluster.phase) + 1) * 0.3
          ctx.fillStyle = `rgba(${index % 2 === 0 ? '125, 211, 252' : '52, 211, 153'}, ${0.28 + nodePulse * 0.28})`
          ctx.beginPath()
          ctx.arc(nx, ny, node.size + nodePulse * 0.7, 0, Math.PI * 2)
          ctx.fill()
        })
      })
      ctx.restore()

      ctx.save()
      ctx.lineWidth = 1
      for(let row = 0; row < (compactMotion ? 3 : 5); row += 1){
        const y = ((height / 8) * (row + 1)) + Math.sin(animatedTime * 0.001 + row) * 10
        const x = ((animatedTime * (0.045 + row * 0.004)) + row * 137) % (width + 220) - 110
        const alpha = 0.07 + (row % 3) * 0.025
        ctx.strokeStyle = `rgba(125, 211, 252, ${alpha})`
        ctx.beginPath()
        ctx.moveTo(x, y)
        ctx.lineTo(x + 92, y)
        ctx.stroke()
      }
      ctx.restore()

      particles.forEach((particle, index)=>{
        particle.x += particle.vx * motionScale
        particle.y += particle.vy * motionScale
        if(particle.x < -20) particle.x = width + 20
        if(particle.x > width + 20) particle.x = -20
        if(particle.y < -20) particle.y = height + 20
        if(particle.y > height + 20) particle.y = -20

        for(let j = index + 1; j < particles.length; j += 1){
          const other = particles[j]
          const dx = particle.x - other.x
          const dy = particle.y - other.y
          const distance = Math.sqrt(dx * dx + dy * dy)
        if(distance < 122){
            const alpha = (1 - distance / 122) * 0.115 * Math.min(particle.depth, other.depth)
            ctx.strokeStyle = `rgba(148, 163, 184, ${alpha})`
            ctx.lineWidth = 1
            ctx.beginPath()
            ctx.moveTo(particle.x, particle.y)
            ctx.lineTo(other.x, other.y)
            ctx.stroke()
          }
        }

        const pulse = 0.5 + (Math.sin(animatedTime * 0.0028 + particle.phase) + 1) * 0.22
        ctx.fillStyle = `rgba(191, 219, 254, ${0.34 * particle.depth * pulse})`
        ctx.beginPath()
        ctx.arc(particle.x, particle.y, particle.radius + particle.depth * 1.2, 0, Math.PI * 2)
        ctx.fill()
      })

      if(!disposed){
        frameId = window.requestAnimationFrame(draw)
      }
    }

    resize()
    frameId = window.requestAnimationFrame(draw)
    window.addEventListener('resize', resize)

    return ()=>{
      disposed = true
      window.cancelAnimationFrame(frameId)
      window.removeEventListener('resize', resize)
    }
  },[disabledOnHome, animatedOnGlobal])

  if(disabledOnHome){
    return null
  }

  if(!animatedOnGlobal){
    return (
      <div className="guardian-ambient-background guardian-ambient-background-static" aria-hidden="true">
        <div className="guardian-ambient-glow guardian-ambient-glow-a" />
        <div className="guardian-ambient-glow guardian-ambient-glow-b" />
        <div className="guardian-ambient-depth" />
      </div>
    )
  }

  return (
    <div className="guardian-ambient-background guardian-ambient-background-global" aria-hidden="true">
      <canvas ref={canvasRef} className="guardian-ambient-canvas" />
      <div className="guardian-ambient-glow guardian-ambient-glow-a" />
      <div className="guardian-ambient-glow guardian-ambient-glow-b" />
      <div className="guardian-ambient-grid" />
      <div className="guardian-ambient-structure" />
      <div className="guardian-ambient-radar" />
      <div className="guardian-ambient-topography" />
      <div className="guardian-ambient-rails" />
      <div className="guardian-ambient-depth" />
      <div className="guardian-ambient-scanlines" />
    </div>
  )
}
