package Elixys.Extended
{
	import Elixys.Events.TransitionCompleteEvent;
	
	import com.danielfreeman.madcomponents.*;
	
	import flash.display.DisplayObject;
	import flash.display.DisplayObjectContainer;
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
		public function CreateLabel(xml:XML):DisplayObject
		{
			return parseLabel(xml, _attributes);
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
		 * Member functions
		 **/
		
		// Loads the next child component.  Return true if loading or false if the load is complete
		public function LoadNext():Boolean
		{
			return false;
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
