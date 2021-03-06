package Elixys.Extended
{
	import Elixys.Assets.Constants;
	import Elixys.Assets.Styling;
	import Elixys.Components.*;
	import Elixys.Interfaces.ITextBox;
	
	import com.danielfreeman.madcomponents.*;
	
	import flash.display.DisplayObject;
	import flash.display.Sprite;
	import flash.events.Event;
	import flash.events.FocusEvent;
	import flash.events.MouseEvent;
	import flash.geom.Point;
	import flash.system.Capabilities;
	import flash.text.engine.FontWeight;
	import flash.utils.*;

	// This input component is an extension of MadComponent's UIInput class
	public class Input extends UIInput
	{
		/***
		 * Construction
		 **/

		public function Input(screen:Sprite, xx:Number, yy:Number, xml:XML, text:String, nLines:int = 1)
		{
			// Call the base constructor
			super(screen, xx, yy, text);

			// Set our size and position
			width = (screen as Form).attributes.width;
			height = (screen as Form).attributes.height;
			x = 0;
			y = 0;
			
			// Create the text input field
			var pTextBox:ITextBox = CreateTextBox(nLines);
			pTextBox.borderColor = 0;
			pTextBox.borderThickness = 1;
			pTextBox.borderCornerSize = 0;
			pTextBox.fontFamily = "HelveticaNeue";
			pTextBox.fontWeight = FontWeight.NORMAL;
			pTextBox.autoCapitalize = Constants.AUTOCAPITALIZE_NONE;
			pTextBox.autoCorrect = false;
			if (xml.@color.length() > 0)
			{
				pTextBox.color = Styling.AS3Color(xml.@color[0]);
			}
			if (xml.@size.length() > 0)
			{
				pTextBox.fontSize = int(xml.@size[0]);
			}
			if (xml.@displayAsPassword.length() > 0)
			{
				pTextBox.displayAsPassword = (xml.@displayAsPassword[0] == "true");
			}

			// Add the new input field
			inputField = pTextBox;
			addChild(pTextBox as DisplayObject);

			// Check if we have a skin
			if (xml.@skin.length() > 0)
			{
				// Disable the text box border
				pTextBox.borderColor = 0xFFFFFF;
				
				// Load the skin
				m_pSkinClass = getDefinitionByName(xml.@skin[0]) as Class;
				m_pSkin = Utils.AddSkin(m_pSkinClass, true, screen, width, height, screen.getChildIndex(this));
			}
			
			// Set the keyboard type and return label after adding it to the display list
			if (xml.@softKeyboardType.length() > 0)
			{
				pTextBox.softKeyboardType = xml.@softKeyboardType[0];
			}
			if (xml.@returnKeyLabel.length() > 0)
			{
				pTextBox.returnKeyLabel = xml.@returnKeyLabel[0];
			}

			// Set the initial text
			if (XML(text).hasSimpleContent())
			{
				_label.text = text;
			}
			else
			{
				_label.htmlText = XML(text).children()[0].toXMLString();
			}
			
			// Add event listeners
			stage.addEventListener(Event.RESIZE, OnResizeEvent);
			addEventListener(Event.ENTER_FRAME, OnEnterFrame);
			
			// Remember the initial dimensions
			m_nLastWidth = width;
			m_nLastHeight = height;
		}
		
		/***
		 * Member functions
		 **/

		// Create the text input field
		protected function CreateTextBox(nLines:int):ITextBox
		{
			// Check where we are running
			if (Capabilities.playerType == "Desktop")
			{
				// This is the AIR player, use native text
				var pNativeTextClass:Class = getDefinitionByName("com.christiancantrell.nativetext::NativeText") as Class;
				var pNativeText:* = new pNativeTextClass(nLines);
				
				// Add the native text to our static array
				m_pNativeTextInputs.push(pNativeText);
				return pNativeText as ITextBox;
			}
			else
			{
				// This is a browser, use basic text box
				return (new TextBox()) as ITextBox;
			}
		}

		// Override the default drawOutline
		protected override function drawOutline(pressed:Boolean = false):void
		{
			// Allow the text box to do the drawing
		}

		// Resize functions to keep the skin size in sync
		protected function OnResizeEvent(event:Event):void
		{
			UpdateSkin();
		}
		protected function OnEnterFrame(event:Event):void
		{
			UpdateSkin();
		}
		protected function UpdateSkin():void
		{
			// Check if our size or position have changed
			var nWidth:Number, nHeight:Number;
			if (m_nFixWidth == -1)
			{
				nWidth = (parent as Form).attributes.width;
			}
			else
			{
				nWidth = m_nFixWidth;
			}
			if (m_nFixHeight == -1)
			{
				nHeight = (parent as Form).attributes.height;
			}
			else
			{
				nHeight = m_nFixHeight;
			}
			if (m_pSkin != null)
			{
				if ((nWidth != m_nLastWidth) || (nHeight != m_nLastHeight) || (x != m_nFixX) || (y != m_nFixY))
				{
					// Set our size and position
					width = nWidth;
					height = nHeight;
					x = m_nFixX;
					y = m_nFixY;

					// Remove and reload the skin to prevent distortion
					parent.removeChild(m_pSkin);
					m_pSkin = Utils.AddSkin(m_pSkinClass, true, parent as Sprite, nWidth, nHeight, parent.getChildIndex(this));

					// Update the skin position
					m_pSkin.x = m_nFixX;
					m_pSkin.y = m_nFixY;
					
					// Remember the new dimensions
					m_nLastWidth = nWidth;
					m_nLastHeight = nHeight;
				}
			}
		}

		// Override visible setter
		public override function set visible(bVisible:Boolean):void
		{
			// Call the base implementation
			super.visible = bVisible;
			
			// Update the skin
			if (m_pSkin != null)
			{
				m_pSkin.visible = bVisible;
			}
		}

		// Fixed size and position
		public function set FixX(value:Number):void
		{
			x = m_nFixX = value;
		}
		public function set FixY(value:Number):void
		{
			y = m_nFixY = value;
		}
		public function set FixWidth(value:Number):void
		{
			width = m_nFixWidth = value;
		}
		public function set FixHeight(value:Number):void
		{
			height = m_nFixHeight = value;
		}

		// Hides the visible native text inputs
		public static function HideNativeTextInputs():void
		{
			// Iterate over our array of native text inputs and hide any that are visible
			var nIndex:int, pNativeText:*;
			for (nIndex = 0; nIndex < m_pNativeTextInputs.length; ++nIndex)
			{
				pNativeText = m_pNativeTextInputs[nIndex];
				if (pNativeText["IsVisible"]())
				{
					pNativeText["visible"] = false;
					m_pHiddenNativeTextInputs.push(pNativeText);
				}
			}
		}

		// Restores the hidden native text inputs
		public static function RestoreNativeTextInputs():void
		{
			// Iterate over our array of hidden native text inputs and restore their visibility
			var nIndex:int, pNativeText:*;
			while (m_pHiddenNativeTextInputs.length)
			{
				pNativeText = m_pHiddenNativeTextInputs.pop();
				pNativeText["visible"] = true;
			}
		}

		/***
		 * Member variables
		 **/
		
		// Skin
		protected var m_pSkin:Sprite;
		protected var m_pSkinClass:Class;
		
		// Fixed offset and size
		protected var m_nFixX:Number = 0;
		protected var m_nFixY:Number = 0;
		protected var m_nFixWidth:Number = -1;
		protected var m_nFixHeight:Number = -1;
		
		// Last known size
		protected var m_nLastWidth:Number = 0;
		protected var m_nLastHeight:Number = 0;

		// Static array of native text elements
		protected static var m_pNativeTextInputs:Array = new Array();
		protected static var m_pHiddenNativeTextInputs:Array = new Array();
	}
}
