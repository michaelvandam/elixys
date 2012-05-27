package com.andymoore
{
	import flash.display.Bitmap;
	import flash.display.BitmapData;
	import flash.display.Sprite;
	import flash.geom.Matrix;
	import flash.geom.Rectangle;
	import flash.utils.getQualifiedClassName;
	/*
	* Author: Shawn Blais ( http://esdot.ca/site/2011/fast-rendering-in-air-3-0-ios-android )
	* Modified by: 01101101 ( http://proceduralactivity.com/blog/ )
	* Further Modified: Andy Moore ( http://www.andymoore.ca )
	* */
	
	public class CachedSprite extends Sprite {
		//Declare a static data cache
		protected static var cachedData:Object = { };
		
		public var clip:Bitmap;
		
		public function CachedSprite(asset:Class, centered:Boolean = false, nScale:Number = 1, nWidth:Number = 0,
									 nHeight:Number = 0)
		{
			//Check the cache to see if we've already cached this asset
			var data:BitmapData = cachedData[getQualifiedClassName(asset) + ":" + Math.ceil(nScale) + ":" + 
				Math.ceil(nWidth) + ":" + Math.ceil(nHeight)];
			
			if (!data) {
				// Not yet cached. Let's do it now
				
				// This should make "Class", "Sprite", and "Bitmap" data types all work.
				var instance:Sprite = new Sprite();
				instance.addChild(new asset());

				// Calculate the scaling
				var nScaleX:Number = nScale, nScaleY:Number = nScale;
				if (nWidth && !nHeight)
				{
					nScaleX = nScaleY = nWidth / instance.width;
				}
				else if (nHeight && !nWidth)
				{
					nScaleX = nScaleY = nHeight / instance.height;
				}
				else if (nWidth && nHeight)
				{
					nScaleX = nWidth / instance.width;
					nScaleY = nHeight / instance.height;
				}

				// Get the bounds of the object in case top-left isn't 0,0
				var bounds:Rectangle = instance.getBounds(this);
				
				// Optionally, use a matrix to up-scale the vector asset,
				// this way you can increase scale later and it still looks good.
				var m:Matrix = new Matrix();
				m.translate(-bounds.x, -bounds.y);
				m.scale(nScaleX, nScaleY);
				
				// This shoves the data to our cache. For mobiles in GPU-rendering mode,
				// also uploads automatically to the GPU as a texture at this point.
				data = new BitmapData(Math.ceil(instance.width * nScaleX), Math.ceil(instance.height * nScaleY), true, 0x0);
				data.draw(instance, m, null, null, null, true); // final true enables smoothing
				
				// Add the bitmap data to our cache
				cachedData[getQualifiedClassName(asset) + ":" + Math.ceil(nScale) + ":" + Math.ceil(nWidth) + ":" + 
					Math.ceil(nHeight)] = data;
			}
			
			// This uses the data already in the GPU texture bank, saving a draw/memory/push call:
			clip = new Bitmap(data, "auto", true);
			
			// Use the bitmap class to inversely scale, so the asset still
			// appear to be it's normal size
			clip.scaleX = clip.scaleY = 1 / nScale;
			
			addChild(clip);
			
			if (centered) {
				// If we want the clip to be centered instead of top-left oriented:
				clip.x = clip.width / -2;
				clip.y = clip.height / -2;
			}
			
			// Optimize mouse children
			mouseChildren = false;
		}
		
		public function kill():void {
			// Just in case you want to clean up things the manual way
			removeChild(clip);
			clip = null;
		}
	}
}
