package Elixys.Extended
{
	import Elixys.Components.*;
	import Elixys.Events.TransitionCompleteEvent;
	
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

		// Creates a new input
		public function CreateInput(pXML:XML, pAttributes:Attributes):Input
		{
			return Input(parseInput(pXML, pAttributes));
		}
		
		// Appends a new child to the display list
		public function AppendChild(pChild:*):void
		{
			_children.push(pChild);
		}

		// Forces the height for use when scrolling
		public function ForceHeight(nHeight:Number):void
		{
			_height = nHeight;
			attributes.height = nHeight;
		}

		// Forces the width for use when scrolling
		public function ForceWidth(nWidth:Number):void
		{
			_width = nWidth;
			attributes.width = nWidth;
		}

		// Walks the display list until a hard width is found
		public static function FindWidth(pDisplayObject:DisplayObject):Number
		{
			// Walk the display list until we get a width value
			var nWidth:Number = 0;
			var pChild:DisplayObject = null;
			while (pDisplayObject != null)
			{
				// Get the current width
				nWidth = pDisplayObject.width;
				
				// Handle form objects
				if (pDisplayObject is Form)
				{
					var pForm:Form = pDisplayObject as Form;
					if (!pForm.attributes.fillH && nWidth)
					{
						break;
					}
					if ((pForm._widths != null) && (pForm._widths.length > 0))
					{
						// Determine the child index
						var nIndex:int = 0;
						for each (var child:DisplayObject in pForm._children)
						{
							if (child == pChild)
							{
								break;
							}
							++nIndex;
						}
						
						// Set the width
						nWidth = pForm._widths[nIndex];
						break;
					}
					if (pForm.attributes.width)
					{
						nWidth = pForm.attributes.width;
						break;
					}
				}
				
				// Move to the parent
				pChild = pDisplayObject;
				pDisplayObject = pDisplayObject.parent;
			}
			
			// Return the width
			return nWidth;
		}
		
		// Walks the display list until a hard height is found
		public static function FindHeight(pDisplayObject:DisplayObject):Number
		{
			// Walk the display list until we get a height value
			var nHeight:Number = 0;
			var pChild:DisplayObject = null;
			while (pDisplayObject != null)
			{
				// Get the current height
				nHeight = pDisplayObject.height;
				
				// Handle form objects
				if (pDisplayObject is Form)
				{
					var pForm:Form = pDisplayObject as Form;
					if (!pForm.attributes.fillV && nHeight)
					{
						break;
					}
					if ((pForm._heights != null) && (pForm._heights.length > 0))
					{
						// Determine the child index
						var nIndex:int = 0;
						for each (var child:DisplayObject in pForm._children)
						{
							if (child == pChild)
							{
								break;
							}
							++nIndex;
						}
							
						// Set the height
						nHeight = pForm._heights[nIndex];
						break;
					}
				}
				
				// Move to the parent
				pChild = pDisplayObject;
				pDisplayObject = pDisplayObject.parent;
			}
			
			// Return the height
			return nHeight;
		}

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
			var inputText:Input = new Input(this, attributes.x, attributes.y, 
				xml, xml.toString());
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
			
			// Refer to the visibility flags of other objects
			if (child is MovieClip)
			{
				return MovieClip(child).visible;
			}
			if (child is UILabel)
			{
				return UILabel(child).visible;
			}
			if (child is Input)
			{
				return Input(child).visible;
			}

			// Include by default
			return true;
		}

		// Width override
		public override function get width():Number
		{
			if (_width > 0)
			{
				return _width;
			}
			else
			{
				return super.width;
			}
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

		// Width override
		protected var _width:Number = -1;
	}
}
