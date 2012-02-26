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
	import flash.system.Capabilities;
	import flash.text.engine.FontWeight;
	import flash.utils.*;

	// This input component is an extension of MadComponent's UIInput class
	public class Input extends UIInput
	{
		/***
		 * Construction
		 **/

		public function Input(screen:Sprite, xx:Number, yy:Number, xml:XML, text:String)
		{
			// Call the base constructor
			super(screen, xx, yy, text);

			// Create the text input field
			var pTextBox:ITextBox = CreateTextBox();
			pTextBox.borderColor = 0;
			pTextBox.borderThickness = 1;
			pTextBox.borderCornerSize = 0;
			pTextBox.fontFamily = "Times New Roman";
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
		}
		
		// Create the text input field
		protected function CreateTextBox():ITextBox
		{
			// Check where we are running
			if (Capabilities.playerType == "Desktop")
			{
				// This is the AIR player, use native text
				var pNativeTextClass:Class = getDefinitionByName("com.christiancantrell.nativetext::NativeText") as Class;
				return (new pNativeTextClass()) as ITextBox;
			}
			else
			{
				// This is a browser, use basic text box
				return (new TextBox()) as ITextBox;
			}
		}

		/***
		 * Overrides
		 **/

		// Override the default drawOutline
		protected override function drawOutline(pressed:Boolean = false):void
		{
			// Allow the text box to do the drawing
		}
	}
}
