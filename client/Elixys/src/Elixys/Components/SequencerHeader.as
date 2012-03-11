package Elixys.Components
{
	import Elixys.Assets.Styling;
	import Elixys.Events.ButtonEvent;
	import Elixys.Extended.Form;
	import Elixys.JSON.State.Column;
	
	import com.danielfreeman.madcomponents.*;
	
	import flash.display.DisplayObject;
	import flash.display.MovieClip;
	import flash.display.Sprite;
	import flash.events.MouseEvent;
	import flash.geom.Point;
	import flash.geom.Rectangle;
	import flash.text.TextFormat;
	import flash.text.TextFormatAlign;
	import flash.utils.*;
	
	// This sequencer header component is an extension of the Form class
	public class SequencerHeader extends Form
	{
		/***
		 * Construction
		 **/
		
		public function SequencerHeader(screen:Sprite, xml:XML, attributes:Attributes = null, row:Boolean = false, inGroup:Boolean = false)
		{
			// Call the base constructor
			super(screen, SEQUENCERHEADER, attributes);
			
			var pButton:DisplayObject = findViewById("test");
			pButton.visible = true;
		}

		/***
		 * Member functions
		 **/
		
		/***
		 * Member variables
					<button id="needed" alignH="fill" alignV="fill" useEmbedded="true"
							enabledTextColor={Styling.TEXT_GRAY1} disabledTextColor={Styling.TEXT_GRAY5}
							backgroundskinup={getQualifiedClassName()}
							backgroundskindown={getQualifiedClassName(sequencer_arrowBtn_down)}
							backgroundskindisabled={getQualifiedClassName(sequencer_arrowBtn_disabled)}>
						<font face="GothamMedium" size="14">
							Sign in
						</font>
					</button>
		 **/
		
		// Datagrid header XML
		protected static const SEQUENCERHEADER:XML = 
			<columns widths="2%,81%,7%,1%,7%,2%" gapH="0">
				<frame />
				<rows heights="15%,85%" gapV="0">
					<frame />
					<label useEmbedded="true">
						<font face="GothamMedium" color={Styling.TEXT_GRAY1} size="20">
							SEQUENCER
						</font>
					</label>
				</rows>
				<frame alignH="fill" alignV="fill" background="#000000">
					<button id="test" alignH="fill" alignV="fill" enabled="true" useEmbedded="true"
							enabledTextColor={Styling.TEXT_GRAY1} disabledTextColor={Styling.TEXT_GRAY5}
							backgroundskinup={getQualifiedClassName(sequencer_arrowBtn_up)}
							backgroundskindown={getQualifiedClassName(sequencer_arrowBtn_down)}
							backgroundskindisabled={getQualifiedClassName(sequencer_arrowBtn_disabled)}>
						<font face="GothamMedium" size="14">
							Sign in
						</font>
					</button>
				</frame>
				<frame />
				<frame background="#0000AA" />
			</columns>;
	}
}
