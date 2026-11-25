import React, { useEffect, useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Compass,
  Eye,
  Film,
  Pause,
  Play,
  Rotate3d,
  RotateCw,
  ShoppingBag,
  Sparkles,
  Volume2,
  VolumeX,
} from 'lucide-react';
import { Button } from '@/components/common/UI';

interface ShortVideoReel {
  id: string;
  title: string;
  brand: string;
  views: string;
  tag: string;
  videoUrl: string;
  posterUrl: string;
  productName: string;
  productSlug: string;
  price: string;
  category: string;
  benefit: string;
  origin: string;
  ingredients: string;
}

const SHORT_REELS: ShortVideoReel[] = [
  {
    id: 'reel-1',
    title: 'Dewy Glass Skin Hydration Routine',
    brand: 'Beauty of Joseon & COSRX',
    views: '1.4M Views',
    tag: 'Trending Viral Reel',
    videoUrl:
      'https://upload.wikimedia.org/wikipedia/commons/3/30/Cosmetics.webmhd.webm',
    posterUrl:
      'https://images.unsplash.com/photo-1620916566398-39f1143ab7be?auto=format&fit=crop&w=800&q=80',
    productName: 'Beauty of Joseon Glow Serum',
    productSlug: 'boj-glow-serum',
    price: '$17.00',
    category: 'Skincare',
    benefit: 'Propolis 60% + Niacinamide 2% pore-refining radiance',
    origin: 'South Korea 🇰🇷',
    ingredients: 'Propolis Extract, Niacinamide, Tamanu Oil, Lotus Corniculatus',
  },
  {
    id: 'reel-2',
    title: 'Velvet Matte Lip Crayon 360° Swatch',
    brand: 'Bella Cosmetics',
    views: '890K Views',
    tag: 'Local Favorite Glam',
    videoUrl:
      'https://upload.wikimedia.org/wikipedia/commons/f/f4/Makeup_demonstration_-_Time_Lapse.webm',
    posterUrl:
      'https://images.unsplash.com/photo-1586495777744-4413f21062fa?auto=format&fit=crop&w=800&q=80',
    productName: 'Bella Matte Velvet Lip Crayon',
    productSlug: 'bella-matte-velvet-lip-crayon',
    price: '$8.50',
    category: 'Makeup',
    benefit: 'Weightless velvet glide with 12-hour comfortable pigment',
    origin: 'Myanmar 🇲🇲',
    ingredients: 'Jojoba Seed Oil, Vitamin E, Candelilla Wax, Botanical Pigments',
  },
  {
    id: 'reel-3',
    title: 'Natural Bark Thanakha Pudding Ritual',
    brand: 'Shwe Pyi Nann',
    views: '2.1M Views',
    tag: 'Heritage Botanical',
    videoUrl:
      'https://upload.wikimedia.org/wikipedia/commons/3/30/Cosmetics.webmhd.webm',
    posterUrl:
      'https://images.unsplash.com/photo-1571781926291-c477ebfd024b?auto=format&fit=crop&w=800&q=80',
    productName: 'Shwe Pyi Nann Natural Bark Thanakha Pudding Face Pack',
    productSlug: 'shwe-pyi-nann-thanakha-pudding',
    price: '$12.50',
    category: 'Skincare',
    benefit: 'Authentic cooling wood-bark herbal mask for pore purification',
    origin: 'Myanmar 🇲🇲',
    ingredients: 'Limonia Acidissima (Thanaka) Bark Powder, Aloe Vera, Vitamin C',
  },
  {
    id: 'reel-4',
    title: 'French Couture Sillage & Gold Mist',
    brand: 'Yves Saint Laurent',
    views: '3.5M Views',
    tag: 'Luxury Icon',
    videoUrl:
      'https://upload.wikimedia.org/wikipedia/commons/f/f4/Makeup_demonstration_-_Time_Lapse.webm',
    posterUrl:
      'https://images.unsplash.com/photo-1592945403244-b3fbafd7f539?auto=format&fit=crop&w=800&q=80',
    productName: 'YSL Libre Eau De Parfum',
    productSlug: 'ysl-libre-eau-de-parfum',
    price: '$98.00',
    category: 'Fragrance',
    benefit: 'French lavender essence and Moroccan orange blossom sillage',
    origin: 'France 🇫🇷',
    ingredients: 'Lavender Diva Essence, Orange Blossom Absolute, Vanilla Bourbon',
  },
];

export const RotatingVideoStudio: React.FC = () => {
  const [activeReelIndex, setActiveReelIndex] = useState(0);
  const activeReel = SHORT_REELS[activeReelIndex];

  // 360-degree rotation states
  const [rotationDegree, setRotationDegree] = useState(0);
  const [isAutoSpinning, setIsAutoSpinning] = useState(true);
  const [spinSpeed, setSpinSpeed] = useState<number>(1); // 0.5x, 1x, 2x
  const [tiltX, setTiltX] = useState(0);

  // Video playback states
  const [isPlaying, setIsPlaying] = useState(true);
  const [isMuted, setIsMuted] = useState(true);
  const [videoError, setVideoError] = useState(false);

  const videoRef = useRef<HTMLVideoElement | null>(null);
  const animFrameRef = useRef<number | null>(null);
  const lastTimeRef = useRef<number>(performance.now());
  const isDraggingRef = useRef(false);
  const startXRef = useRef(0);
  const startRotationRef = useRef(0);

  // Continuous smooth 360-degree turntable rotation animation
  useEffect(() => {
    if (!isAutoSpinning) {
      if (animFrameRef.current) cancelAnimationFrame(animFrameRef.current);
      return;
    }

    const animate = (currentTime: number) => {
      const delta = currentTime - lastTimeRef.current;
      lastTimeRef.current = currentTime;

      // 360 degrees rotation loop (roughly 30 deg/sec at 1x)
      const step = (30 * spinSpeed * delta) / 1000;
      setRotationDegree((prev) => (prev + step) % 360);

      animFrameRef.current = requestAnimationFrame(animate);
    };

    lastTimeRef.current = performance.now();
    animFrameRef.current = requestAnimationFrame(animate);

    return () => {
      if (animFrameRef.current) cancelAnimationFrame(animFrameRef.current);
    };
  }, [isAutoSpinning, spinSpeed]);

  // Video play/pause effect
  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;

    if (isPlaying) {
      try {
        const playPromise = video.play();
        if (playPromise && typeof playPromise.catch === 'function') {
          playPromise.catch(() => {
            // Autoplay policy fallback: mute and retry
            video.muted = true;
            setIsMuted(true);
            const retryPromise = video.play();
            if (retryPromise && typeof retryPromise.catch === 'function') {
              retryPromise.catch(() => setVideoError(true));
            }
          });
        }
      } catch {
        setVideoError(true);
      }
    } else {
      try {
        video.pause();
      } catch {
        // ignore
      }
    }
  }, [isPlaying, activeReelIndex]);

  // Mouse / Touch Drag to Rotate in 360 Degrees
  const handlePointerDown = (e: React.PointerEvent<HTMLDivElement>) => {
    isDraggingRef.current = true;
    startXRef.current = e.clientX;
    startRotationRef.current = rotationDegree;
    setIsAutoSpinning(false);
  };

  const handlePointerMove = (e: React.PointerEvent<HTMLDivElement>) => {
    if (!isDraggingRef.current) return;
    const deltaX = e.clientX - startXRef.current;
    const newDegree = (startRotationRef.current + deltaX * 0.8) % 360;
    setRotationDegree(newDegree < 0 ? newDegree + 360 : newDegree);
  };

  const handlePointerUp = () => {
    isDraggingRef.current = false;
  };

  // Card side determination (0-90 or 270-360 is front, 90-270 is back)
  const normalizedDeg = ((rotationDegree % 360) + 360) % 360;
  const isBackSide = normalizedDeg > 90 && normalizedDeg < 270;

  return (
    <section
      aria-labelledby="video-studio-heading"
      className="relative overflow-hidden rounded-3xl border border-border bg-gradient-to-br from-card via-blush/20 to-beige/40 p-6 shadow-sm sm:p-10"
    >
      {/* Decorative ambient background glows */}
      <div
        aria-hidden="true"
        className="pointer-events-none absolute -left-20 -top-20 h-72 w-72 rounded-full bg-blush/60 blur-3xl"
      />
      <div
        aria-hidden="true"
        className="pointer-events-none absolute -bottom-20 -right-20 h-72 w-72 rounded-full bg-primary/10 blur-3xl"
      />

      {/* Header Banner */}
      <div className="relative z-10 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div className="space-y-1.5">
          <div className="inline-flex items-center gap-2 rounded-full border border-primary/20 bg-primary/10 px-3.5 py-1 text-xs font-semibold uppercase tracking-wider text-primary">
            <Rotate3d className="h-3.5 w-3.5" aria-hidden="true" />
            <span>Interactive 360° Studio</span>
          </div>
          <h2 id="video-studio-heading" className="font-serif text-3xl font-bold sm:text-4xl">
            Popular Beauty in Motion · 360° Rotating Studio
          </h2>
          <p className="max-w-2xl text-sm text-muted-fg">
            Explore trending cosmetic short reels in full 360-degree rotation. Drag the turntable
            or use the slider to inspect finishes, swatches, and formulation specs from every angle.
          </p>
        </div>

        {/* 360 Control Toolbar */}
        <div className="flex flex-wrap items-center gap-2">
          <Button
            variant={isAutoSpinning ? 'primary' : 'outline'}
            onClick={() => setIsAutoSpinning((prev) => !prev)}
            className="touch-target inline-flex items-center gap-1.5 px-3 py-1.5 text-xs"
            aria-pressed={isAutoSpinning}
          >
            <RotateCw className={`h-3.5 w-3.5 ${isAutoSpinning ? 'animate-spin' : ''}`} />
            <span>{isAutoSpinning ? 'Auto-Spin ON' : 'Auto-Spin OFF'}</span>
          </Button>

          <Button
            variant="outline"
            onClick={() => {
              setRotationDegree(0);
              setTiltX(0);
              setIsAutoSpinning(false);
            }}
            className="touch-target inline-flex items-center gap-1 px-3 py-1.5 text-xs"
          >
            <Compass className="h-3.5 w-3.5" />
            <span>Reset 0°</span>
          </Button>

          <div className="flex items-center rounded-lg border border-border bg-card px-2 py-1 text-xs font-mono">
            <span className="text-muted-fg mr-1.5">Angle:</span>
            <span className="font-semibold text-primary">{Math.round(rotationDegree)}°</span>
          </div>
        </div>
      </div>

      {/* Main Studio Grid */}
      <div className="relative z-10 mt-8 grid gap-8 lg:grid-cols-12 lg:items-center">
        {/* LEFT COLUMN: 360° 3D Rotating Video Turntable Card (7 Cols) */}
        <div className="lg:col-span-7 flex flex-col items-center">
          {/* 3D Perspective Stage */}
          <div
            className="relative w-full max-w-md select-none touch-none cursor-grab active:cursor-grabbing"
            style={{ perspective: '1200px' }}
            onPointerDown={handlePointerDown}
            onPointerMove={handlePointerMove}
            onPointerUp={handlePointerUp}
            onPointerLeave={handlePointerUp}
          >
            {/* The 3D Rotating Card Container */}
            <div
              className="relative aspect-[9/14] w-full rounded-2xl border border-border bg-card shadow-2xl transition-transform duration-75"
              style={{
                transformStyle: 'preserve-3d',
                transform: `rotateY(${rotationDegree}deg) rotateX(${tiltX}deg)`,
              }}
            >
              {/* FRONT SIDE (0° - 90° & 270° - 360°) - Active Video Player */}
              <div
                className="absolute inset-0 overflow-hidden rounded-2xl bg-card"
                style={{
                  backfaceVisibility: 'hidden',
                }}
              >
                {!videoError ? (
                  <video
                    ref={videoRef}
                    key={activeReel.id}
                    src={activeReel.videoUrl}
                    poster={activeReel.posterUrl}
                    playsInline
                    muted={isMuted}
                    loop
                    className="h-full w-full object-cover"
                    onError={() => setVideoError(true)}
                  />
                ) : (
                  <div className="relative h-full w-full">
                    <img
                      src={activeReel.posterUrl}
                      alt={activeReel.title}
                      className="h-full w-full object-cover"
                    />
                    <div className="absolute inset-0 bg-black/30 flex items-center justify-center">
                      <span className="rounded-full bg-card/90 px-4 py-2 text-xs font-semibold text-foreground">
                        High-Definition Preview Reel
                      </span>
                    </div>
                  </div>
                )}

                {/* Video Overlays: Top Header Tag */}
                <div className="absolute left-4 right-4 top-4 flex items-center justify-between">
                  <span className="rounded-full bg-card/85 px-3 py-1 text-xs font-semibold backdrop-blur-md text-foreground">
                    {activeReel.tag}
                  </span>
                  <span className="rounded-full bg-black/60 px-2.5 py-0.5 text-[11px] font-mono text-white backdrop-blur-md">
                    {activeReel.views}
                  </span>
                </div>

                {/* Video Play/Pause & Audio Floating Overlay Controls */}
                <div className="absolute right-4 top-1/2 -translate-y-1/2 flex flex-col gap-2.5 z-20">
                  <button
                    type="button"
                    onClick={(e) => {
                      e.stopPropagation();
                      setIsPlaying((prev) => !prev);
                    }}
                    className="touch-target flex h-10 w-10 items-center justify-center rounded-full bg-card/90 text-foreground shadow-md transition-transform hover:scale-110 active:scale-95"
                    aria-label={isPlaying ? 'Pause video' : 'Play video'}
                  >
                    {isPlaying ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4 fill-current" />}
                  </button>

                  <button
                    type="button"
                    onClick={(e) => {
                      e.stopPropagation();
                      setIsMuted((prev) => !prev);
                    }}
                    className="touch-target flex h-10 w-10 items-center justify-center rounded-full bg-card/90 text-foreground shadow-md transition-transform hover:scale-110 active:scale-95"
                    aria-label={isMuted ? 'Unmute video' : 'Mute video'}
                  >
                    {isMuted ? <VolumeX className="h-4 w-4" /> : <Volume2 className="h-4 w-4" />}
                  </button>
                </div>

                {/* Bottom Glassmorphism Product Capsule Tag */}
                <div className="absolute bottom-4 left-4 right-4 rounded-xl border border-border/80 bg-card/90 p-3.5 backdrop-blur-md shadow-lg">
                  <div className="flex items-center justify-between gap-2 text-[11px] text-muted-fg">
                    <span className="font-semibold uppercase tracking-wider text-primary">
                      {activeReel.brand}
                    </span>
                    <span>{activeReel.origin}</span>
                  </div>
                  <h3 className="line-clamp-1 font-serif text-sm font-bold text-foreground">
                    {activeReel.productName}
                  </h3>
                  <div className="mt-2 flex items-center justify-between">
                    <span className="font-mono text-sm font-bold text-foreground">
                      {activeReel.price}
                    </span>
                    <Link
                      to={`/products/${activeReel.productSlug}`}
                      className="touch-target inline-flex items-center gap-1.5 rounded-lg bg-primary px-3 py-1.5 text-xs font-semibold text-primary-fg transition-opacity hover:opacity-90"
                    >
                      <ShoppingBag className="h-3.5 w-3.5" />
                      <span>Shop Look</span>
                    </Link>
                  </div>
                </div>

                {/* Drag 360 instruction watermark */}
                <div className="pointer-events-none absolute left-0 right-0 top-16 text-center text-[10px] font-semibold uppercase tracking-wider text-white/80 drop-shadow">
                  ⟵ Drag horizontally to spin 360° ⟶
                </div>
              </div>

              {/* BACK SIDE (90° - 270°) - Formulation Specs & 360 Depth View */}
              <div
                className="absolute inset-0 flex flex-col justify-between rounded-2xl border border-primary/30 bg-gradient-to-br from-card via-beige/80 to-blush/60 p-6 text-foreground"
                style={{
                  backfaceVisibility: 'hidden',
                  transform: 'rotateY(180deg)',
                }}
              >
                <div>
                  <div className="flex items-center justify-between text-xs text-primary font-semibold">
                    <span className="inline-flex items-center gap-1">
                      <Sparkles className="h-3.5 w-3.5" />
                      <span>360° Formulation Specs</span>
                    </span>
                    <span>180° Back Profile</span>
                  </div>

                  <h3 className="mt-3 font-serif text-xl font-bold">{activeReel.productName}</h3>
                  <p className="mt-1 text-xs text-muted-fg">{activeReel.brand} · {activeReel.origin}</p>

                  <div className="mt-5 space-y-3">
                    <div className="rounded-lg border border-border bg-card/80 p-3">
                      <span className="block text-[10px] uppercase font-semibold text-muted-fg tracking-wider">
                        Key Benefit
                      </span>
                      <p className="mt-0.5 text-xs font-medium text-foreground">{activeReel.benefit}</p>
                    </div>

                    <div className="rounded-lg border border-border bg-card/80 p-3">
                      <span className="block text-[10px] uppercase font-semibold text-muted-fg tracking-wider">
                        Active Ingredients
                      </span>
                      <p className="mt-0.5 text-xs font-mono text-muted-fg leading-relaxed">
                        {activeReel.ingredients}
                      </p>
                    </div>

                    <div className="grid grid-cols-2 gap-2 text-center text-xs">
                      <div className="rounded-lg border border-border bg-card/80 p-2">
                        <span className="block text-[10px] text-muted-fg">Customer Love</span>
                        <span className="font-bold text-primary">★ 4.9 / 5.0</span>
                      </div>
                      <div className="rounded-lg border border-border bg-card/80 p-2">
                        <span className="block text-[10px] text-muted-fg">Batch Expiry</span>
                        <span className="font-bold text-success font-mono">Verified Safe</span>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="mt-4 pt-3 border-t border-border flex items-center justify-between">
                  <div>
                    <span className="block text-[10px] text-muted-fg">Price</span>
                    <span className="font-mono text-base font-bold text-foreground">{activeReel.price}</span>
                  </div>
                  <Link
                    to={`/products/${activeReel.productSlug}`}
                    className="touch-target inline-flex items-center gap-2 rounded-xl bg-primary px-4 py-2 text-xs font-semibold text-primary-fg shadow-sm transition-opacity hover:opacity-90"
                  >
                    <ShoppingBag className="h-4 w-4" />
                    <span>View Product</span>
                  </Link>
                </div>
              </div>
            </div>

            {/* Dynamic 360° Studio Shadow/Glow under turntable */}
            <div
              className="mx-auto mt-4 h-5 w-3/4 rounded-full bg-primary/20 blur-lg transition-transform duration-75"
              style={{
                transform: `scaleX(${1 + Math.sin((rotationDegree * Math.PI) / 180) * 0.2})`,
              }}
            />
          </div>

          {/* Interactive 360 Turntable Scrub Slider */}
          <div className="mt-5 w-full max-w-md rounded-2xl border border-border bg-card p-4 shadow-sm">
            <div className="flex items-center justify-between text-xs font-medium text-foreground mb-1.5">
              <span className="inline-flex items-center gap-1.5 text-primary">
                <Rotate3d className="h-4 w-4" />
                <span>360° Turntable Angle</span>
              </span>
              <span className="font-mono text-xs font-bold text-foreground">
                {Math.round(rotationDegree)}° ({isBackSide ? 'Back Angle' : 'Front Angle'})
              </span>
            </div>

            <input
              type="range"
              min="0"
              max="360"
              step="1"
              value={Math.round(rotationDegree)}
              onChange={(e) => {
                setIsAutoSpinning(false);
                setRotationDegree(Number(e.target.value));
              }}
              className="h-2 w-full cursor-pointer appearance-none rounded-lg bg-beige accent-primary"
              aria-label="Rotate video 360 degrees slider"
            />

            <div className="mt-3 flex items-center justify-between text-[11px] text-muted-fg">
              <div className="flex gap-1.5">
                {[0, 90, 180, 270, 360].map((deg) => (
                  <button
                    key={deg}
                    type="button"
                    onClick={() => {
                      setIsAutoSpinning(false);
                      setRotationDegree(deg % 360);
                    }}
                    className="rounded border border-border px-2 py-0.5 font-mono text-[10px] hover:border-primary hover:text-primary transition-colors"
                  >
                    {deg}°
                  </button>
                ))}
              </div>

              <div className="flex items-center gap-1 font-mono text-[10px]">
                <span className="text-muted-fg">Speed:</span>
                {[0.5, 1, 2].map((s) => (
                  <button
                    key={s}
                    type="button"
                    onClick={() => setSpinSpeed(s)}
                    className={`rounded px-1.5 py-0.5 ${
                      spinSpeed === s ? 'bg-primary text-primary-fg font-bold' : 'text-muted-fg hover:text-foreground'
                    }`}
                  >
                    {s}x
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* RIGHT COLUMN: Trending Video Reels Selector (5 Cols) */}
        <div className="lg:col-span-5 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-serif text-xl font-bold flex items-center gap-2">
              <Film className="h-4 w-4 text-primary" />
              <span>Trending Beauty Reels</span>
            </h3>
            <span className="text-xs text-muted-fg font-mono">
              {activeReelIndex + 1} of {SHORT_REELS.length}
            </span>
          </div>

          <div className="space-y-3">
            {SHORT_REELS.map((reel, idx) => {
              const isActive = idx === activeReelIndex;
              return (
                <button
                  key={reel.id}
                  type="button"
                  onClick={() => {
                    setActiveReelIndex(idx);
                    setVideoError(false);
                    setIsPlaying(true);
                  }}
                  className={`group w-full text-left rounded-2xl border p-3.5 transition-all duration-200 cursor-pointer flex items-center gap-3.5 ${
                    isActive
                      ? 'border-primary bg-card shadow-md scale-[1.02]'
                      : 'border-border bg-card/60 hover:bg-card hover:border-primary/40'
                  }`}
                >
                  {/* Thumbnail */}
                  <div className="relative h-16 w-14 shrink-0 overflow-hidden rounded-xl border border-border bg-beige">
                    <img
                      src={reel.posterUrl}
                      alt={reel.title}
                      className="h-full w-full object-cover transition-transform duration-300 group-hover:scale-105"
                    />
                    <div className="absolute inset-0 bg-black/20 flex items-center justify-center">
                      <Play className="h-4 w-4 fill-white text-white drop-shadow" />
                    </div>
                  </div>

                  {/* Reel details */}
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center justify-between gap-1 text-[11px] text-muted-fg">
                      <span className="font-semibold uppercase tracking-wider text-primary line-clamp-1">
                        {reel.brand}
                      </span>
                      <span className="shrink-0">{reel.views}</span>
                    </div>

                    <h4 className="line-clamp-1 text-sm font-semibold text-foreground group-hover:text-primary transition-colors">
                      {reel.title}
                    </h4>

                    <div className="mt-1 flex items-center justify-between text-xs">
                      <span className="text-muted-fg text-[11px] line-clamp-1">{reel.productName}</span>
                      <span className="font-mono font-bold text-foreground shrink-0">{reel.price}</span>
                    </div>
                  </div>
                </button>
              );
            })}
          </div>

          {/* Quick Value Callout Box */}
          <div className="rounded-2xl border border-border bg-card/80 p-4 text-xs text-muted-fg space-y-1.5">
            <div className="flex items-center gap-1.5 font-semibold text-foreground">
              <Eye className="h-4 w-4 text-primary" />
              <span>360° Studio Tip</span>
            </div>
            <p>
              Rotate the card beyond 90° to flip over and review verified active ingredients, batch
              expiration safety, and dermatologist certifications before adding to your bag.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
};
