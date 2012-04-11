package Elixys.Components
{
	import Elixys.Interfaces.ITextBox;
	
	import flash.text.TextField;
	import flash.text.TextFieldType;
	import flash.text.TextFormat;
	
	// This button component is browser-compatible version of ITextBox
	public class TextBox extends TextField implements ITextBox
	{
		/***
		 * Construction
		 **/

		public function TextBox()
		{
			// Editable by default
			editable = true;
		}

		/***
		 * ITextBox interface functions
		 **/

		public override function addEventListener(type:String, listener:Function, useCapture:Boolean=false, priority:int=0, 
												  useWeakReference:Boolean=false):void
		{
			super.addEventListener(type, listener, useCapture, priority, useWeakReference);
		}
		public override function removeEventListener(type:String, listener:Function, useCapture:Boolean=false):void
		{
			super.removeEventListener(type, listener, useCapture);
		}
		public override function set border(border:Boolean):void
		{
			super.border = border;
		}
		public function set borderThickness(borderThickness:uint):void
		{
			// Not supported 
		}
		public function get borderThickness():uint
		{
			// Not supported 
			return 0;
		}
		public override function set borderColor(borderColor:uint):void
		{
			super.borderColor = borderColor;
		}
		public override function get borderColor():uint
		{
			return super.borderColor;
		}
		public function set borderCornerSize(borderCornerSize:uint):void
		{
			// Not supported 
		}
		public function get borderCornerSize():uint
		{
			// Not supported 
			return 0;
		}
		public function set autoCapitalize(autoCapitalize:String):void
		{
			// Not supported 
		}
		public function set autoCorrect(autoCorrect:Boolean):void
		{
			// Not supported 
		}
		public function set color(color:uint):void
		{
			super.textColor = color;
		}
		public function containsInternally(object:*):Boolean
		{
			// Not supported at the moment
			return false;
		}
		public override function set displayAsPassword(displayAsPassword:Boolean):void
		{
			super.displayAsPassword = displayAsPassword;
		}
		public function set editable(editable:Boolean):void
		{
			if (editable)
			{
				super.type = TextFieldType.INPUT;
			}
			else
			{
				super.type = TextFieldType.DYNAMIC;
			}
		}
		public function set fontFamily(fontFamily:String):void
		{
			m_pTextFormat.font = fontFamily;
			super.setTextFormat(m_pTextFormat);
		}
		public function set fontPosture(fontPosture:String):void
		{
		}
		public function set fontSize(fontSize:uint):void
		{
			m_pTextFormat.size = fontSize;
			super.setTextFormat(m_pTextFormat);
		}
		public function set fontWeight(fontWeight:String):void
		{
			m_pTextFormat.bold = (fontWeight.toLowerCase().search("bold") >= 0);
			super.setTextFormat(m_pTextFormat);
		}
		public function set locale(locale:String):void
		{
			// Not supported
		}
		public override function set maxChars(maxChars:int):void
		{
			super.maxChars = maxChars;
		}
		public override function set restrict(restrict:String):void
		{
			super.restrict = restrict;
		}
		public function set returnKeyLabel(returnKeyLabel:String):void
		{
			// Not supported
		}
		public function get selectionActiveIndex():int
		{
			return 0;
		}
		public function get selectionAnchorIndex():int
		{
			return 0;
		}
		public function set softKeyboardType(softKeyboardType:String):void
		{
			// This has no meaning for a text field
		}
		public override function get text():String
		{
			return super.text;
		}
		public override function set text(text:String):void
		{
			super.text = text;
		}
		public function set textAlign(textAlign:String):void
		{
		}
		public override function set visible(visible:Boolean):void
		{
			super.visible = visible;
		}
		public override function get multiline():Boolean
		{
			return super.multiline;
		}
		public function assignFocus():void
		{
		}
		public function selectRange(anchorIndex:int, activeIndex:int):void
		{
			// Not supported
		}
		public override function set width(width:Number):void
		{
			super.width = width;
		}
		public override function get width():Number
		{
			return super.width;
		}
		public function set fixwidth(value:Number):void
		{
			super.width = value;
		}
		public override function set height(height:Number):void
		{
			super.height = height;
		}
		public override function get height():Number
		{
			return super.height;
		}
		public override function set x(x:Number):void
		{
			super.x = x;
		}
		public override function set y(y:Number):void
		{
			super.y = y;
		}

		/***
		 * Member variables
		 **/

		// Text format
		protected var m_pTextFormat:TextFormat = new TextFormat();
		protected var m_nBorderThickness:uint = 0;
	}
}
