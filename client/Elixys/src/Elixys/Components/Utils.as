package Elixys.Components
{
	import Elixys.Extended.Form;
	
	import com.andymoore.CachedSprite;
	import com.danielfreeman.madcomponents.UILabel;
	
	import flash.display.Sprite;
	import flash.text.TextFormat;
	import flash.text.TextFormatAlign;

	// This utils class wraps a number of shared operations
	public class Utils
	{
		// Add a skin targets to a given width and height
		public static function AddSkin(pClass:Class, bVisible:Boolean, pParent:Sprite,
									   nWidth:Number = 0, nHeight:Number = 0, nIndex:int = -1,
									   nX:Number = 0, nY:Number = 0):Sprite
		{
			var pSkin:CachedSprite = new CachedSprite(pClass, false, 1, nWidth, nHeight);
			pSkin.visible = bVisible;
			if (nIndex == -1)
			{
				nIndex = pParent.numChildren;
			}
			pParent.addChildAt(pSkin, nIndex);
			pSkin.x = nX;
			pSkin.y = nY;
			return pSkin as Sprite;
		}

		// Add a skin targets to a given scale
		public static function AddSkinScale(pClass:Class, bVisible:Boolean, pParent:Sprite,
										    nScale:Number = 1, nIndex:int = -1):Sprite
		{
			var pSkin:CachedSprite = new CachedSprite(pClass, false, nScale, 0, 0);
			pSkin.visible = bVisible;
			if (nIndex == -1)
			{
				nIndex = pParent.numChildren;
			}
			pParent.addChildAt(pSkin, nIndex);
			return pSkin as Sprite;
		}

		// Adds a text label
		public static function AddLabel(sText:String, pForm:Form, sFontFace:String, nFontSize:int,
										nTextColor:uint, pParent:Sprite = null):UILabel
		{
			var pXML:XML =
				<label useEmbedded="true" alignH="left" alignV="bottom">
					<font face={sFontFace} size={nFontSize} />
				</label>;
			var pLabel:UILabel = pForm.CreateLabel(pXML, pForm.attributes);
			if (pParent != null)
			{
				pForm.removeChild(pLabel);
				pParent.addChild(pLabel);
			}
			pLabel.textColor = nTextColor;
			pLabel.text = sText;
			pLabel.multiline = false;
			pLabel.wordWrap = false;
			return pLabel;
		}
	}
}
