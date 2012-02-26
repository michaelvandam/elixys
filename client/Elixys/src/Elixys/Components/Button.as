package Elixys.Components
{
	import Elixys.Assets.Styling;
	import Elixys.Extended.*;
	
	import com.danielfreeman.madcomponents.*;
	
	import flash.display.DisplayObject;
	import flash.display.MovieClip;
	import flash.display.Sprite;
	import flash.events.Event;
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
				_label = UILabel((screen as Form).CreateLabel(xml, new Attributes(0, 0, width, height)));
				_label.parent.removeChild(_label);
				addChild(_label);
			}

			// Disable the hand cursor
			useHandCursor = false;

			// Determine our current width and height
			var nWidth:int = Form.FindWidth(screen);
			var nHeight:int = Form.FindHeight(screen);

			// Set the skins
			if (xml.@skinup.length() > 0)
			{
				m_pSkinUp = AddSkin(xml.@skinup[0]);
				Form.PositionSkin(m_pSkinUp, nWidth, nHeight);
			}
			if (xml.@skindown.length() > 0)
			{
				m_pSkinDown = AddSkin(xml.@skindown[0]);
				Form.PositionSkin(m_pSkinDown, nWidth, nHeight);
			}
			if (xml.@skindisabled.length() > 0)
			{
				m_pSkinDisabled = AddSkin(xml.@skindisabled[0]);
				Form.PositionSkin(m_pSkinDisabled, nWidth, nHeight);
			}
			
			// Set the enabled flag
			if (xml.@enabled.length() > 0)
			{
				enabled = (xml.@enabled[0] == "true");
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

			// Remember our initial dimensions
			m_nLastWidth = nWidth;
			m_nLastHeight = nHeight;
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

		// Add a skin
		protected function AddSkin(sClassName:String):MovieClip
		{
			var pClass:Class = getDefinitionByName(sClassName) as Class;
			var pSkin:MovieClip = new pClass() as MovieClip;
			pSkin.buttonMode = false;
			pSkin.addEventListener(MouseEvent.MOUSE_DOWN, OnMouseDown);
			pSkin.addEventListener(MouseEvent.MOUSE_UP, OnMouseUp);
			addChild(pSkin);
			return pSkin;
		}

		// Positions the skin
		protected function PositionSkin(pSkin:MovieClip, nWidth:int, nHeight:int):void
		{
			pSkin.width = nWidth;
			pSkin.height = nHeight;
		}
		
		// Refreshes the button
		public function Refresh():void
		{
			// Check if our dimensions have changed
			if ((width != m_nLastWidth) || (height != m_nLastHeight))
			{
				// Update the skins
				if (m_pSkinUp != null)
				{
					PositionSkin(m_pSkinUp, width, height);
				}
				if (m_pSkinDown != null)
				{
					PositionSkin(m_pSkinDown, width, height);
				}
				if (m_pSkinDisabled != null)
				{
					PositionSkin(m_pSkinDisabled, width, height);
				}
				
				// Remember the new dimensions
				m_nLastWidth = width;
				m_nLastHeight = height;
			}
			
			// Draw the button
			drawButton();
		}
		
		// Overridden drawing function
		protected override function drawButton(pressed:Boolean = false):void
		{
			// Check if we have background skins
			if ((m_pSkinUp != null) && (m_pSkinDown != null))
			{
				// Clear anything that may have been drawn
				graphics.clear();
				
				// Check if we have a disabled skin
				if (m_pSkinDisabled != null)
				{
					// Check if we are enabled
					if (!m_bEnabled)
					{
						// Set our state to disabled
						m_pSkinUp.visible = false;
						m_pSkinDown.visible = false;
						m_pSkinDisabled.visible = true;
					}
					else
					{
						// Set our state to enabled
						m_pSkinDisabled.visible = false;
					}
				}
				
				// Show either the up or down skin if we're enabled
				if (m_bEnabled)
				{
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
				
				// Make sure the text is centered over the skins
				_label.x = (m_pSkinUp.width - _label.width) / 2;
				_label.y = (m_pSkinUp.height - _label.height) / 2;
			}
			else
			{
				// Call the default implementation if we didn't have any skins
				super.drawButton(pressed);
			}
			
			// Set the text color
			if (m_bEnabled)
			{
				_label.textColor = m_nEnabledTextColor;
			}
			else
			{
				_label.textColor = m_nDisabledTextColor;
			}
		}

		// Called when the user presses the mouse button
		protected function OnMouseDown(event:MouseEvent):void
		{
			if (m_bEnabled)
			{
				drawButton(true);
			}
		}
		
		// Called when the user releases the mouse button
		protected function OnMouseUp(event:MouseEvent):void
		{
			if (m_bEnabled)
			{
				drawButton(false);
				dispatchEvent(new Event(BUTTON_CLICK));
			}
		}
		
		/***
		 * Member variables
		 **/
		
		// Button click event
		public static var BUTTON_CLICK:String = "ButtonClick";

		// Skins
		protected var m_pSkinUp:MovieClip;
		protected var m_pSkinDown:MovieClip;
		protected var m_pSkinDisabled:MovieClip;
		
		// Button enabled flag
		protected var m_bEnabled:Boolean = true;
		
		// Text colors
		protected var m_nEnabledTextColor:uint;
		protected var m_nDisabledTextColor:uint;
		
		// Last know dimensions
		protected var m_nLastWidth:int;
		protected var m_nLastHeight:int;
	}
}
