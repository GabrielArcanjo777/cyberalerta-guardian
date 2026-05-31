"use client"

import React, {useEffect, useRef} from 'react'

type Particle = {
  x:number
  y:number
  vx:number
  vy:number
  depth:number
  phase:number
  radius:number
}

export default function GlobalAmbientBackground(){
  const canvasRef = useRef<HTMLCanvasElement | null>(null)

  useEffect(()=>{
    const canvas = canvasRef.current
    if(!canvas) return

    const activeCanvas = canvas
    const context = activeCanvas.getContext('2d')
    if(!context) return
    const ctx = context

    const media = window.matchMedia('(prefers-reduced-motion: reduce)')
    const reducedMotion = media.matches
    const particles:Particle[] = []
    let width = 0
    let height = 0
    let dpr = 1
    let frameId = 0
    let disposed = false

    function createParticles(){
      particles.length = 0
      const count = Math.min(132, Math.max(64, Math.floor((width * height) / 14000)))
      for(let i = 0; i < count; i += 1){
        const depth = 0.35 + Math.random() * 0.65
        particles.push({
          x: Math.random() * width,
          y: Math.random() * height,
          vx: (Math.random() - 0.5) * 0.28 * depth,
          vy: (Math.random() - 0.5) * 0.22 * depth,
          depth,
          phase: Math.random() * Math.PI * 2,
          radius: 0.9 + Math.random() * 1.9,
        })
      }
    }

    function resize(){
      const rect = activeCanvas.getBoundingClientRect()
      width = Math.max(1, rect.width)
      height = Math.max(1, rect.height)
      dpr = Math.min(window.devicePixelRatio || 1, 2)
      activeCanvas.width = Math.floor(width * dpr)
      activeCanvas.height = Math.floor(height * dpr)
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0)
      createParticles()
    }

    function draw(time:number){
      ctx.clearRect(0, 0, width, height)

      const sweep = ((time * 0.018) % (width + 420)) - 210
      const secondarySweep = width - ((time * 0.012) % (width + 520))
      const glowA = ctx.createRadialGradient(width * 0.18, height * 0.16, 0, width * 0.18, height * 0.16, Math.max(width, height) * 0.42)
      glowA.addColorStop(0, 'rgba(56, 189, 248, 0.12)')
      glowA.addColorStop(0.44, 'rgba(56, 189, 248, 0.04)')
      glowA.addColorStop(1, 'rgba(56, 189, 248, 0)')
      ctx.fillStyle = glowA
      ctx.fillRect(0, 0, width, height)

      const glowB = ctx.createRadialGradient(width * 0.82, height * 0.52, 0, width * 0.82, height * 0.52, Math.max(width, height) * 0.5)
      glowB.addColorStop(0, 'rgba(34, 197, 94, 0.075)')
      glowB.addColorStop(0.4, 'rgba(34, 197, 94, 0.025)')
      glowB.addColorStop(1, 'rgba(34, 197, 94, 0)')
      ctx.fillStyle = glowB
      ctx.fillRect(0, 0, width, height)

      ctx.save()
      ctx.lineWidth = 1
      ctx.strokeStyle = 'rgba(125, 211, 252, 0.08)'
      for(let i = 0; i < 4; i += 1){
        const offset = i * 80
        ctx.beginPath()
        ctx.moveTo(sweep - offset, 0)
        ctx.lineTo(sweep + 140 - offset, height)
        ctx.stroke()
      }

      ctx.strokeStyle = 'rgba(34, 197, 94, 0.055)'
      for(let i = 0; i < 3; i += 1){
        const offset = i * 120
        ctx.beginPath()
        ctx.moveTo(secondarySweep + offset, 0)
        ctx.lineTo(secondarySweep - 160 + offset, height)
        ctx.stroke()
      }
      ctx.restore()

      particles.forEach((particle, index)=>{
        if(!reducedMotion){
          particle.x += particle.vx
          particle.y += particle.vy
          if(particle.x < -20) particle.x = width + 20
          if(particle.x > width + 20) particle.x = -20
          if(particle.y < -20) particle.y = height + 20
          if(particle.y > height + 20) particle.y = -20
        }

        for(let j = index + 1; j < particles.length; j += 1){
          const other = particles[j]
          const dx = particle.x - other.x
          const dy = particle.y - other.y
          const distance = Math.sqrt(dx * dx + dy * dy)
          if(distance < 125){
            const alpha = (1 - distance / 125) * 0.13 * Math.min(particle.depth, other.depth)
            ctx.strokeStyle = `rgba(148, 163, 184, ${alpha})`
            ctx.lineWidth = 1
            ctx.beginPath()
            ctx.moveTo(particle.x, particle.y)
            ctx.lineTo(other.x, other.y)
            ctx.stroke()
          }
        }

        const pulse = reducedMotion ? 0.65 : 0.52 + (Math.sin(time * 0.002 + particle.phase) + 1) * 0.18
        ctx.fillStyle = `rgba(191, 219, 254, ${0.23 * particle.depth * pulse})`
        ctx.beginPath()
        ctx.arc(particle.x, particle.y, particle.radius + particle.depth * 1.2, 0, Math.PI * 2)
        ctx.fill()
      })

      if(!disposed && !reducedMotion){
        frameId = window.requestAnimationFrame(draw)
      }
    }

    resize()
    draw(0)
    if(!reducedMotion){
      frameId = window.requestAnimationFrame(draw)
    }
    window.addEventListener('resize', resize)

    return ()=>{
      disposed = true
      window.cancelAnimationFrame(frameId)
      window.removeEventListener('resize', resize)
    }
  },[])

  return (
    <div className="guardian-ambient-background" aria-hidden="true">
      <canvas ref={canvasRef} className="guardian-ambient-canvas" />
      <div className="guardian-ambient-glow guardian-ambient-glow-a" />
      <div className="guardian-ambient-glow guardian-ambient-glow-b" />
      <div className="guardian-ambient-grid" />
      <div className="guardian-ambient-depth" />
      <div className="guardian-ambient-scanlines" />
    </div>
  )
}
