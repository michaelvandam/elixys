package Elixys.Interfaces
{
	public interface ITextBox
	{
		function set borderThickness(borderThickness:uint):void;
		function get borderThickness():uint;
		function set borderColor(borderColor:uint):void;
		function get borderColor():uint;
		function set borderCornerSize(borderCornerSize:uint):void;
		function get borderCornerSize():uint;
		function set autoCapitalize(autoCapitalize:String):void;
		function set autoCorrect(autoCorrect:Boolean):void;
		function set color(color:uint):void;
		function set displayAsPassword(displayAsPassword:Boolean):void;
		function set editable(editable:Boolean):void;
		function set fontFamily(fontFamily:String):void;
		function set fontPosture(fontPosture:String):void;
		function set fontSize(fontSize:uint):void;
		function set fontWeight(fontWeight:String):void;
		function set locale(locale:String):void;
		function set maxChars(maxChars:int):void;
		function set restrict(restrict:String):void;
		function set returnKeyLabel(returnKeyLabel:String):void;
		function get selectionActiveIndex():int;
		function get selectionAnchorIndex():int;
		function set softKeyboardType(softKeyboardType:String):void;
		function get text():String;
		function set text(text:String):void;
		function set textAlign(textAlign:String):void;
		function set visible(visible:Boolean):void;
		function get multiline():Boolean;
		function assignFocus():void;
		function selectRange(anchorIndex:int, activeIndex:int):void;
		function set width(width:Number):void;
		function get width():Number;
		function set fixwidth(value:Number):void;
		function set height(height:Number):void;
		function get height():Number;
		function set x(x:Number):void;
		function set y(y:Number):void;
	}
}
