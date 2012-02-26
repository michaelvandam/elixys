package Elixys.Extended
{
	import Elixys.Events.TransitionCompleteEvent;
	import Elixys.Components.*;
	
	import com.danielfreeman.madcomponents.*;
	
	import flash.display.DisplayObject;
	import flash.display.DisplayObjectContainer;
	import flash.display.MovieClip;
	import flash.display.Sprite;
	import flash.events.TimerEvent;
	import flash.text.AntiAliasType;
	import flash.text.TextFormat;
	import flash.utils.Timer;

	// This form component is an extension of MadComponent's UIForm class
	public class Form extends UIForm
	{
		/***
		 * Construction
		 **/
		
		public function Form(screen:Sprite, xml:XML, attributes:Attributes = null, row:Boolean = false, inGroup:Boolean = false)
		{
			// Call the base constructor
			super(screen, xml, attributes, row, inGroup);
		}
		
		/***
		 * Member functions
		 **/
		
		// Creates a new label
		public function CreateLabel(pXML:XML, pAttributes:Attributes):UILabel
		{
			return UILabel(parseLabel(pXML, pAttributes));
		}

		// Appends a new child to the display list
		public function AppendChild(pChild:*):void
		{
			_children.push(pChild);
		}

		// Locates the main application in the display tree
		public function GetMainApplication():Elixys
		{
			// Walk the tree and find the main application
			if (m_pElixys == null)
			{
				var pDOC:DisplayObjectContainer = this;
				while (!(pDOC is Elixys) && (pDOC != null))
				{
					pDOC = pDOC.parent;
				}
				if (pDOC != null)
				{
					m_pElixys = pDOC as Elixys;
				}
			}
			return m_pElixys;
		}
		
		// Walks the display list until a hard width is found
		public static function FindWidth(pDisplayObject:DisplayObject):int
		{
			// Walk the display list until we get a width value
			while (pDisplayObject.width == 0)
			{
				pDisplayObject = pDisplayObject.parent;
				if (pDisplayObject == null)
				{
					throw Error("Failed to determine object width");
				}
			}
			
			// Return the width
			return pDisplayObject.width;
		}
		
		// Walks the display list until a hard height is found
		public static function FindHeight(pDisplayObject:DisplayObject):int
		{
			// Walk the display list until we get a height value
			while (pDisplayObject.height == 0)
			{
				pDisplayObject = pDisplayObject.parent;
				if (pDisplayObject == null)
				{
					throw Error("Failed to determine object height");
				}
			}
			
			// Return the height
			return pDisplayObject.height;
		}

		// Set the movie clip position so it covers the entire form
		public static function PositionSkin(pSkin:MovieClip, nWidth:int, nHeight:int):void
		{
			pSkin.x = 0;
			pSkin.y = 0;
			pSkin.width = nWidth;
			pSkin.height = nHeight;
		}

		// Set the movie clip and text positions so they are centered over the button and scaled to the specified percent
		// width or height
		public static function PositionSkinAndLabel(pButton:Button, pSkin:MovieClip, pLabel:UILabel, nSkinWidthPercent:int, 
			nSkinHeightPercent:int):void
		{
			// Determine the skin width and height
			var nSkinWidth:int, nSkinHeight:int;
			if (nSkinWidthPercent != 0)
			{
				nSkinWidth = pSkin.parent.width * nSkinWidthPercent / 100;
				nSkinHeight = nSkinWidth * (pSkin.height / pSkin.width);
			}
			else
			{
				nSkinHeight = pSkin.parent.height * nSkinHeightPercent / 100;
				nSkinWidth = nSkinHeight * (pSkin.width / pSkin.height);
			}

			// Determine the scaled skin position
			var nSkinX:int = ((pButton.width - nSkinWidth) / 2);
			var nSkinY:int = ((pButton.height - nSkinHeight) / 2);
			
			// Set theskin position
			pSkin.x = nSkinX + pButton.x;
			pSkin.y = nSkinY + pButton.y;
			pSkin.width = nSkinWidth;
			pSkin.height = nSkinHeight;
			trace("  Skin " + pSkin + " is (" + pSkin.width + ", " + pSkin.height + ") with scale (" + pSkin.scaleX + ", " +
				pSkin.scaleY + ") is located at (" + pSkin.x + ", " + pSkin.y + ")");
		}

		/*
		// Set the movie clip and text positions so they are centered over the form and scaled to the specified percent
		// width or height
		public static function PositionSkinAndLabel(pSkin:MovieClip, pLabel:UILabel, nWidth:int, nHeight:int, 
													nScaleX:Number, nScaleY:Number, nSkinWidthPercent:int, nSkinHeightPercent:int):void
		{
			var nGap:int = 4;
			trace("Position skin center");
			trace("  Parent " + pSkin.parent + " is (" + nWidth + ", " + nHeight + ") with scale (" + nScaleX + ", " + nScaleY + ")");
			trace("  Skin " + pSkin + " is (" + pSkin.width + ", " + pSkin.height + ") with scale (" + pSkin.scaleX + ", " +
			pSkin.scaleY + ") is located at (" + pSkin.x + ", " + pSkin.y + ")");
			
			
			// Determine the skin width and height in scaled parent dimensions
			var nSkinWidthScaled:int, nSkinHeightScaled:int;
			if (nSkinWidthPercent != 0)
			{
				nSkinWidthScaled = nWidth * nSkinWidthPercent / 100;
				nSkinHeightScaled = nSkinWidthScaled * (pSkin.height / pSkin.scaleY) / (pSkin.width / pSkin.scaleX);
			}
			else
			{
				nSkinHeightScaled = nHeight * nSkinHeightPercent / 100;
				nSkinWidthScaled = nSkinHeightScaled * (pSkin.width / pSkin.scaleX) / (pSkin.height / pSkin.scaleY);
			}
			
			if (pLabel.text == "SEQUENCER")
			{
				trace("pLabel.textHeight = " + pLabel.textHeight);
			}
			// Determine the scaled skin position
			var nSkinXScaled:int = ((nWidth - nSkinWidthScaled) / 2);
			var nSkinYScaled:int = ((nHeight - nSkinHeightScaled) / 2) - (pLabel.textHeight / 2) - (nGap / 2);
			
			// Set the unscaled skin position
			pSkin.x = nSkinXScaled / nScaleX;
			pSkin.y = nSkinYScaled / nScaleY;
			pSkin.width = nSkinWidthScaled / nScaleX;
			pSkin.height = nSkinHeightScaled / nScaleY;
			
			// Determine the scaled label position
			var nLabelXScaled:int = ((nWidth - pLabel.textWidth) / 2);
			var nLabelYScaled:int = nSkinYScaled + nSkinHeightScaled + nGap;
			
			// Set the unscaled text position
			pLabel.x = pSkin.x;	//nLabelXScaled / nScaleX;
			pLabel.y = pSkin.y;	//nLabelYScaled / nScaleY;
			pLabel.scaleX = pSkin.width;	//1 / nScaleX;
			pLabel.scaleY = pSkin.height;	//1 / nScaleY;
			//pLabel.width = pLabel.textWidth / nScaleX;
			//pLabel.height = pLabel.textHeight / nScaleY;
			
			trace("  Skin " + pSkin + " is (" + pSkin.width + ", " + pSkin.height + ") with scale (" + pSkin.scaleX + ", " +
			pSkin.scaleY + ") is located at (" + pSkin.x + ", " + pSkin.y + ")");
		}
		*/

		/***
		 * Overrides
		 **/

		// Override the default parseLabel function so we can enable embedded fonts
		protected override function parseLabel(xml:XML, attributes:Attributes):DisplayObject
		{
			// Call the base handler to create the label
			var pLabel:UILabel = super.parseLabel(xml, attributes) as UILabel;

			// Check if this label is tagged as embedded
			if (xml.@useEmbedded == "true")
			{
				// Enable embedded fonts and crank up the anti-aliasing
				pLabel.embedFonts = true;
				pLabel.antiAliasType = AntiAliasType.ADVANCED;
			}
			return pLabel;
		}
		
		// Override the default parseInput function so we can use our version
		protected override function parseInput(xml:XML, attributes:Attributes):DisplayObject
		{
			var inputText:Input = new Input(this, attributes.x, attributes.y, xml, xml.toString());
			if (attributes.fillH) 
			{
				inputText.fixwidth = attributes.widthH;
			}
			return inputText;
		}

		// Override the default parseButton function so we can use our version
		protected override function parseButton(xml:XML, attributes:Attributes):DisplayObject
		{
			var button:Button = new Button(this, attributes.x, attributes.y, xml, attributes.colour, 
				attributes.backgroundColours, xml.@alt.length()>0);
			if (xml.@skin.length()>0)
			{
				button.skin = xml.@skin[0];
			}
			if (attributes.fillH)
			{
				button.fixwidth = attributes.widthH;
			}
			if (attributes.fillV)
			{
				button.skinHeight = attributes.heightV;
			}
			return button;
		}

		// Determine if the display object should be included in MadComponent's layout
		protected override function included(child:DisplayObject):Boolean
		{
			// Refer to MadSprite's include flag
			if (child is MadSprite)
			{
				return MadSprite(child).includeInLayout;
			}
			
			// Refer to MovieClip's visibility flag
			if (child is MovieClip)
			{
				return MovieClip(child).visible;
			}
			
			// Include by default
			return true;
		}


		/***
		 * Transitions
		 **/
		
		// Fade transition
		public function Fade(fStartAlpha:Number, fEndAlpha:Number, nAnimationTime:uint):void
		{
			if (!m_bInTransition)
			{
				// Set the fade variables
				m_bInTransition = true;
				var nAnimationSteps:uint = nAnimationTime / Elixys.TRANSITION_UPDATE_INTERVAL;
				m_fAlphaStep = (fEndAlpha - fStartAlpha) / nAnimationSteps;
				m_fEndAlpha = fEndAlpha;
				
				// Set the initial visibility and transparency
				if (fEndAlpha > 0)
				{
					visible = true;
				}
				alpha = fStartAlpha;
				
				// Start the fade in timer
				m_pFadeTimer = new Timer(Elixys.TRANSITION_UPDATE_INTERVAL, nAnimationSteps);
				m_pFadeTimer.addEventListener(TimerEvent.TIMER, OnFadeTimer);
				m_pFadeTimer.addEventListener(TimerEvent.TIMER_COMPLETE, OnFadeTimerComplete);
				m_pFadeTimer.start();
			}
		}
		protected function OnFadeTimer(event:TimerEvent):void
		{
			// Update the transparency
			alpha += m_fAlphaStep;
		}
		protected function OnFadeTimerComplete(event:TimerEvent):void
		{
			// Set the final transparency
			if (m_fEndAlpha == 0)
			{
				visible = false;
			}
			alpha = m_fEndAlpha;
			
			// Clear the transition flag and dispatch the completion event
			m_bInTransition = false;
			dispatchEvent(new TransitionCompleteEvent(this));
		}
		
		/***
		 * Member variables
		 **/
		
		// Transition flag
		protected var m_bInTransition:Boolean = false;
		
		// Fade transition variables
		protected var m_fAlphaStep:Number = 0;
		protected var m_fEndAlpha:Number = 0;
		protected var m_pFadeTimer:Timer;
		
		// Main Elixys application
		protected var m_pElixys:Elixys;
	}
}
