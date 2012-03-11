package Elixys.Components
{
	import Elixys.Assets.Styling;
	import Elixys.Events.ButtonEvent;
	import Elixys.Extended.*;
	
	import com.danielfreeman.madcomponents.*;
	
	import flash.display.DisplayObject;
	import flash.display.MovieClip;
	import flash.display.Sprite;
	import flash.events.Event;
	import flash.events.MouseEvent;
	import flash.geom.Point;
	import flash.geom.Rectangle;
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
			if (parent is Form)
			{
				var pAttributes:Attributes = new Attributes(0, 0, width, height);
				pAttributes.parse(xml);
				_label = UILabel((screen as Form).CreateLabel(xml, pAttributes));
				_label.parent.removeChild(_label);
				addChild(_label);
				_label.width = _label.textWidth + 5;
				_label.height = _label.textHeight;
			}
			
			// Disable the hand cursor
			useHandCursor = false;

			// Determine the width and height of our parent
			var nWidth:int = 0;
			var nHeight:int = 0;
			if (parent is Form)
			{
				nWidth = (screen as Form).attributes.width;
				nHeight = (screen as Form).attributes.height;
			}
			
			// Set the foreground skins
			if (xml.@foregroundskinup.length() > 0)
			{
				m_pForegroundSkinUp = AddSkin(xml.@foregroundskinup[0]);
				PositionForegroundSkin(m_pForegroundSkinUp, m_pBackgroundSkinUp);
			}
			if (xml.@foregroundskindown.length() > 0)
			{
				m_pForegroundSkinDown = AddSkin(xml.@foregroundskindown[0]);
				PositionForegroundSkin(m_pForegroundSkinDown, m_pBackgroundSkinDown);
			}
			if (xml.@foregroundskindisabled.length() > 0)
			{
				m_pForegroundSkinDisabled = AddSkin(xml.@foregroundskindisabled[0]);
				PositionForegroundSkin(m_pForegroundSkinDisabled, m_pBackgroundSkinDisabled);
			}

			// Set the background skins
			if (xml.@backgroundskinup.length() > 0)
			{
				m_pBackgroundSkinUp = AddSkin(xml.@backgroundskinup[0]);
				PositionBackgroundSkin(m_pBackgroundSkinUp, nWidth, nHeight);
			}
			if (xml.@backgroundskindown.length() > 0)
			{
				m_pBackgroundSkinDown = AddSkin(xml.@backgroundskindown[0]);
				PositionBackgroundSkin(m_pBackgroundSkinDown, nWidth, nHeight);
			}
			if (xml.@backgroundskindisabled.length() > 0)
			{
				m_pBackgroundSkinDisabled = AddSkin(xml.@backgroundskindisabled[0]);
				PositionBackgroundSkin(m_pBackgroundSkinDisabled, nWidth, nHeight);
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

			// Add event listeners
			stage.addEventListener(Event.RESIZE, OnResizeEvent);
			addEventListener(Event.ENTER_FRAME, OnEnterFrame);
			
			// Listen for click events from the base class if we don't have skins
			if ((m_pBackgroundSkinUp == null) || (m_pBackgroundSkinDown == null))
			{
				addEventListener(UIButton.CLICKED, OnBaseClassClick);
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

		// Add a skin
		protected function AddSkin(sClassName:String):MovieClip
		{
			var pClass:Class = getDefinitionByName(sClassName) as Class;
			var pSkin:MovieClip = new pClass() as MovieClip;
			pSkin.buttonMode = false;
			pSkin.addEventListener(MouseEvent.MOUSE_DOWN, OnMouseDown);
			addChildAt(pSkin, 0);
			return pSkin;
		}

		// Positions the background or foreground skin
		protected function PositionBackgroundSkin(pSkin:MovieClip, nWidth:int, nHeight:int):void
		{
			pSkin.width = nWidth;
			pSkin.height = nHeight;
		}
		protected function PositionForegroundSkin(pSkin:MovieClip, pBackgroundSkin:MovieClip):void
		{
			pSkin.x = pBackgroundSkin.x + ((pBackgroundSkin.width - pSkin.width) / 2);
			pSkin.y = pBackgroundSkin.y + ((pBackgroundSkin.height - pSkin.height) / 2);
		}

		// Resize functions to keep the skin sizes in sync
		protected function OnResizeEvent(event:Event):void
		{
			UpdateSkins();
		}
		protected function OnEnterFrame(event:Event):void
		{
			UpdateSkins();
		}
		protected function UpdateSkins():void
		{
			// Check if our size or position have changed
			if (parent is Form)
			{
				var nWidth:int = (parent as Form).attributes.width;
				var nHeight:int = (parent as Form).attributes.height;
				if ((nWidth != m_nLastWidth) || (nHeight != m_nLastHeight) || (x != m_nLastX) || (y != m_nLastY))
				{
					// Update the size and position
					m_nLastX = x;
					m_nLastY = y;
					m_nLastWidth = nWidth;
					m_nLastHeight = nHeight;
						
					// Update the background skins
					if (m_pBackgroundSkinUp != null)
					{
						PositionBackgroundSkin(m_pBackgroundSkinUp, nWidth, nHeight);
					}
					if (m_pBackgroundSkinDown != null)
					{
						PositionBackgroundSkin(m_pBackgroundSkinDown, nWidth, nHeight);
					}
					if (m_pBackgroundSkinDisabled != null)
					{
						PositionBackgroundSkin(m_pBackgroundSkinDisabled, nWidth, nHeight);
					}

					// Update the foreground skins
					if (m_pForegroundSkinUp != null)
					{
						PositionForegroundSkin(m_pForegroundSkinUp, m_pBackgroundSkinUp);
					}
					if (m_pForegroundSkinDown != null)
					{
						PositionForegroundSkin(m_pForegroundSkinDown, m_pBackgroundSkinDown);
					}
					if (m_pForegroundSkinDisabled != null)
					{
						PositionForegroundSkin(m_pForegroundSkinDisabled, m_pBackgroundSkinDisabled);
					}

					// Make sure the text is centered
					if (m_pBackgroundSkinUp != null)
					{
						_label.x = (m_pBackgroundSkinUp.width - _label.width) / 2;
						_label.y = (m_pBackgroundSkinUp.height - _label.height) / 2;
					}
					
					// Draw the button
					drawButton();
				}
			}
		}
		
		// Overridden drawing function
		protected override function drawButton(pressed:Boolean = false):void
		{
			// Check if we have background skins
			if ((m_pBackgroundSkinUp != null) && (m_pBackgroundSkinDown != null))
			{
				// Clear anything that may have been drawn
				graphics.clear();
				
				// Check if we have a disabled skin
				if (m_pBackgroundSkinDisabled != null)
				{
					// Check if we are enabled
					if (!m_bEnabled)
					{
						// Set our state to disabled
						m_pBackgroundSkinUp.visible = false;
						m_pBackgroundSkinDown.visible = false;
						m_pBackgroundSkinDisabled.visible = true;
					}
					else
					{
						// Set our state to enabled
						m_pBackgroundSkinDisabled.visible = false;
					}
				}
				
				// Show either the up or down skin if we're enabled
				if (m_bEnabled)
				{
					if (pressed)
					{
						m_pBackgroundSkinUp.visible = false;
						m_pBackgroundSkinDown.visible = true;
					}
					else
					{
						m_pBackgroundSkinUp.visible = true;
						m_pBackgroundSkinDown.visible = false;
					}
				}
				
				// Set the foreground skin visibility
				if (m_pForegroundSkinUp != null)
				{
					m_pForegroundSkinUp.visible = m_pBackgroundSkinUp.visible;
				}
				if (m_pForegroundSkinDown != null)
				{
					m_pForegroundSkinDown.visible = m_pBackgroundSkinDown.visible;
				}
				if (m_pForegroundSkinDisabled != null)
				{
					m_pForegroundSkinDisabled.visible = m_pBackgroundSkinDisabled.visible;
				}
				
				for (var i:int = 0; i < this.numChildren; ++i)
				{
					var pChild:DisplayObject = getChildAt(i);
					trace("Child " + i + ": " + pChild + " (x = " + pChild.x + ", y = " + pChild.y + ", width = " + pChild.width +
						", height = " + pChild.height + ", visible = " + pChild.visible + ")");
				}
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
				// Remember the hit area in global coordinates
				var pUpperLeft:Point = new Point(event.target.x, event.target.y);
				var pLowerRight:Point = new Point(event.target.x + event.target.width, event.target.y + event.target.height);
				pUpperLeft = localToGlobal(pUpperLeft);
				pLowerRight = localToGlobal(pLowerRight);
				m_pMouseHitRect.x = pUpperLeft.x;
				m_pMouseHitRect.y = pUpperLeft.y;
				m_pMouseHitRect.width = pLowerRight.x - pUpperLeft.x;
				m_pMouseHitRect.height = pLowerRight.y - pUpperLeft.y;
				
				// Listen for mouse up
				stage.addEventListener(MouseEvent.MOUSE_UP, OnMouseUp);
				
				// Draw the button as pressed
				drawButton(true);
			}
		}
		
		// Called when the user releases the mouse button
		protected function OnMouseUp(event:MouseEvent):void
		{
			// Remove the event listener
			stage.removeEventListener(MouseEvent.MOUSE_UP, OnMouseUp);

			// Check if the mouse was released over the button
			if (m_pMouseHitRect.contains(event.stageX, event.stageY))
			{
				// Dispatch a click event
				dispatchEvent(new ButtonEvent(name));
			}

			// Draw the button as released
			drawButton(false);
		}
		
		// Called when the base class is doing the rendering and the button is clicked
		protected function OnBaseClassClick(event:Event):void
		{
			dispatchEvent(new ButtonEvent(name));
		}
		
		// Override the text setter
		public override function set text(value:String):void
		{
			// Set the label size to the maximum
			_label.width = width;
			_label.height = height;
			
			// Call the base setter
			super.text = value;
			
			// Adjust the label size to slightly larger than the text
			_label.width = _label.textWidth + 5;
			_label.height = _label.textHeight;
			_label.x = (width - _label.width) / 2;
			_label.y = (height - _label.height) / 2;
		}
		
		/***
		 * Member variables
		 **/

		// Skins
		protected var m_pBackgroundSkinUp:MovieClip;
		protected var m_pBackgroundSkinDown:MovieClip;
		protected var m_pBackgroundSkinDisabled:MovieClip;
		protected var m_pForegroundSkinUp:MovieClip;
		protected var m_pForegroundSkinDown:MovieClip;
		protected var m_pForegroundSkinDisabled:MovieClip;
		
		// Button enabled flag
		protected var m_bEnabled:Boolean = true;
		
		// Text colors
		protected var m_nEnabledTextColor:uint;
		protected var m_nDisabledTextColor:uint;
		
		// Last known size and position
		protected var m_nLastX:Number = 0;
		protected var m_nLastY:Number = 0;
		protected var m_nLastWidth:Number = 0;
		protected var m_nLastHeight:Number = 0;
		
		// Mouse hit area
		protected var m_pMouseHitRect:Rectangle = new Rectangle();
	}
}
