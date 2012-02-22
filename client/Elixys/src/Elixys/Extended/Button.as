package Elixys.Extended
{
	import Elixys.Assets.Styling;
	
	import com.danielfreeman.madcomponents.*;
	
	import flash.display.MovieClip;
	import flash.display.Sprite;
	import flash.events.MouseEvent;
	import flash.text.TextFormatAlign;
	import flash.utils.*;

	// This button component is an extension of MadComponent's UIButton class
	public class Button extends UIButton
	{
		/***
		 * Construction
		 **/

		public function Button(screen:Sprite, xx:Number, yy:Number, xml:XML, colour:uint = 0x9999AA, 
								 colours:Vector.<uint> = null, tiny:Boolean = false)
		{
			// Call the base constructor
			super(screen, xx, yy, xml.toString(), colour, colours, tiny);

			// Remove the base constructor's labels
			removeChild(_shadowLabel);
			removeChild(_label);

			// Create a new label that implenents embedded fonts
			if (screen is Form)
			{
				_label = UILabel((screen as Form).CreateLabel(xml));
				_label.parent.removeChild(_label);
				addChild(_label);
			}
			
			// Set the skins
			var pClass:Class;
			if (xml.@skinup.length() > 0)
			{
				pClass = getDefinitionByName(xml.@skinup[0]) as Class;
				m_pSkinUp = new pClass() as MovieClip;
				m_pSkinUp.visible = false;
				addChildAt(m_pSkinUp, 0);
			}
			if (xml.@skindown.length() > 0)
			{
				pClass = getDefinitionByName(xml.@skindown[0]) as Class;
				m_pSkinDown = new pClass() as MovieClip;
				m_pSkinDown.visible = false;
				addChildAt(m_pSkinDown, 0);
			}
			if (xml.@skindisabled.length() > 0)
			{
				pClass = getDefinitionByName(xml.@skindisabled[0]) as Class;
				m_pSkinDisabled = new pClass() as MovieClip;
				m_pSkinDisabled.visible = false;
				addChildAt(m_pSkinDisabled, 0);
			}
			
			// Set the enabled flag
			if (xml.@enabled.length() > 0)
			{
				m_bEnabled = (xml.@enabled[0] == "true");
			}

			// Set the text colors
			if (xml.@enabledTextColor.length() > 0)
			{
				m_nEnabledTextColor = Styling.AS3Color(xml.@enabledTextColor[0]);
			}
			if (xml.@disabledTextColor.length() > 0)
			{
				m_nDisabledTextColor = Styling.AS3Color(xml.@disabledTextColor[0]);
			}
		}

		/***
		 * Member functions
		 **/
		
		// Gets and sets the enabled state
		public function set enabled(value:Boolean):void
		{
			m_bEnabled = value;
			drawButton();
		}
		public function get enabled():Boolean
		{
			return m_bEnabled;
		}
		
		// Overridden drawing function
		protected override function drawButton(pressed:Boolean = false):void
		{
			// Check if we have up and down skins
			if ((m_pSkinUp == null) || (m_pSkinDown == null))
			{
				// Call the base implementation
				return super.drawButton(pressed);
			}
			
			// Clear anything that may have been drawn
			graphics.clear();

			// Make sure the text is centered over the up skin
			_label.x = (m_pSkinUp.width - _label.width) / 2;
			_label.y = (m_pSkinUp.height - _label.height) / 2;

			// Check if we have a disabled skin
			if (m_pSkinDisabled != null)
			{
				// Check if we're disabled
				if (!m_bEnabled)
				{
					// Set our state to disabled and return
					m_pSkinDisabled.visible = true;
					m_pSkinUp.visible = false;
					m_pSkinDown.visible = false;
					_label.textColor = m_nDisabledTextColor;
					return;
				}
				else
				{
					// Set our state to enabled
					m_pSkinDisabled.visible = false;
					_label.textColor = m_nEnabledTextColor;
				}
			}
			
			// Show either the up or down skin
			if (pressed)
			{
				m_pSkinUp.visible = false;
				m_pSkinDown.visible = true;
			}
			else
			{
				m_pSkinUp.visible = true;
				m_pSkinDown.visible = false;
			}
		}

		/***
		 * Member variables
		 **/
		
		// Skins
		protected var m_pSkinUp:MovieClip;
		protected var m_pSkinDown:MovieClip;
		protected var m_pSkinDisabled:MovieClip;
		
		// Button enabled flag
		protected var m_bEnabled:Boolean;
		
		// Text colors
		protected var m_nEnabledTextColor:uint;
		protected var m_nDisabledTextColor:uint;
	}
}
