"""
ComfyUI native sampler wrapper for model-agnostic upscaling
"""
import torch
import comfy.sample
import comfy.utils


class ComfyUISamplerWrapper:
    """
    Wrapper for ComfyUI's native sampling system
    
    This replaces the FLUX-specific pipeline with model-agnostic sampling
    that works with any diffusion model supported by ComfyUI.
    """
    
    def __init__(self, model, vae, clip=None):
        """
        Initialize with ComfyUI MODEL and VAE
        
        Args:
            model: ComfyUI MODEL object
            vae: ComfyUI VAE object  
            clip: Optional CLIP model for text conditioning
        """
        self.model = model
        self.vae = vae
        self.clip = clip
        
    def encode_image(self, image_tensor):
        """
        Encode image to latent space using VAE
        
        Args:
            image_tensor: Image tensor in ComfyUI format [B, H, W, C]
            
        Returns:
            Latent tensor [B, C, H//8, W//8]
        """
        # Convert from ComfyUI format [B, H, W, C] to VAE format [B, C, H, W]
        pixels = image_tensor.movedim(-1, 1)
        
        # Encode to latent
        latent = self.vae.encode(pixels[:, :, :, :])
        
        return latent
    
    def decode_latent(self, latent):
        """
        Decode latent to image using VAE
        
        Args:
            latent: Latent tensor [B, C, H//8, W//8]
            
        Returns:
            Image tensor in ComfyUI format [B, H, W, C]
        """
        # Decode from latent
        pixels = self.vae.decode(latent)
        
        # Convert back to ComfyUI format [B, C, H, W] -> [B, H, W, C]
        image = pixels.movedim(1, -1)
        
        return image
    
    def upscale(
        self,
        image,
        scale_factor=2.0,
        denoise=0.4,
        steps=20,
        cfg=7.0,
        sampler_name="euler",
        scheduler="normal",
        positive_conditioning=None,
        negative_conditioning=None,
        seed=0,
        dino_features=None
    ):
        """
        Upscale image using ComfyUI's native sampling
        
        Args:
            image: PIL Image or numpy array
            scale_factor: Upscaling factor
            denoise: Denoising strength (0.0-1.0)
            steps: Number of sampling steps
            cfg: CFG scale
            sampler_name: Sampler algorithm
            scheduler: Noise schedule
            positive_conditioning: Positive CONDITIONING from CLIP
            negative_conditioning: Negative CONDITIONING from CLIP
            seed: Random seed
            dino_features: Optional DINO features (not yet used)
            
        Returns:
            Upscaled PIL Image
        """
        from PIL import Image
        import numpy as np
        
        # Convert input to tensor
        if isinstance(image, Image.Image):
            image = np.array(image)
        
        if isinstance(image, np.ndarray):
            # Convert numpy to tensor [H, W, C] -> [B, H, W, C]
            image_tensor = torch.from_numpy(image).float() / 255.0
            if image_tensor.ndim == 3:
                image_tensor = image_tensor.unsqueeze(0)
        else:
            image_tensor = image
        
        # Encode to latent
        latent = self.encode_image(image_tensor)
        
        # Upscale latent using bicubic
        h, w = latent.shape[2:]
        new_h = int(h * scale_factor)
        new_w = int(w * scale_factor)
        
        upscaled_latent = torch.nn.functional.interpolate(
            latent,
            size=(new_h, new_w),
            mode='bicubic',
            align_corners=False
        )
        
        # Prepare latent dict for sampling
        latent_dict = {"samples": upscaled_latent}
        
        # Prepare conditioning
        if positive_conditioning is None:
            # Create empty conditioning if none provided
            positive_conditioning = [[torch.zeros((1, 77, 768)), {}]]
        if negative_conditioning is None:
            negative_conditioning = [[torch.zeros((1, 77, 768)), {}]]
        
        # Sample using ComfyUI's native sampler
        batch_inds = latent_dict.get("batch_index", None)
        noise = comfy.sample.prepare_noise(upscaled_latent, seed, batch_inds)
        
        samples = comfy.sample.sample(
            self.model,
            noise,
            steps,
            cfg,
            sampler_name,
            scheduler,
            positive_conditioning,
            negative_conditioning,
            upscaled_latent,
            denoise=denoise,
            disable_noise=False,
            start_step=None,
            last_step=None,
            force_full_denoise=True,
            noise_mask=None,
            callback=None,
            disable_pbar=False,
            seed=seed
        )
        
        # Decode back to image
        result_image = self.decode_latent(samples)
        
        # Convert to PIL
        result_np = (result_image[0].cpu().numpy() * 255).astype(np.uint8)
        result_pil = Image.fromarray(result_np)
        
        return result_pil
