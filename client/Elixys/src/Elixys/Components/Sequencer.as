package Elixys.Components
{
	import Elixys.Assets.Styling;
	import Elixys.Events.ButtonEvent;
	import Elixys.Events.SelectionEvent;
	import Elixys.Extended.Form;
	import Elixys.JSON.Components.ComponentBase;
	import Elixys.JSON.State.Sequence;
	
	import com.danielfreeman.madcomponents.*;
	
	import flash.display.MovieClip;
	import flash.display.Sprite;
	import flash.utils.*;
	
	// This sequencer component is an extension of our extended Form class
	public class Sequencer extends Form
	{
		/***
		 * Construction
		 **/
		
		public function Sequencer(screen:Sprite, xml:XML, attributes:Attributes, nUnitOperationWidth:Number,
								  nButtonSkinWidth:Number)
		{
			// Determine our current width and height
			var nWidth:int = Form.FindWidth(screen);
			var nHeight:int = Form.FindHeight(screen);

			// Add the background skin
			m_pBackgroundSkin = AddSkin(sequencer_windowBackground);
			m_pBackgroundSkin.width = nWidth;
			m_pBackgroundSkin.height = nHeight;

			// Get our mode
			if (xml.@mode.length() > 0)
			{
				m_sMode = xml.@mode[0];
				SEQUENCER.sequencerheader[0].@mode = m_sMode;
				SEQUENCER.sequencerbody[0].@mode = m_sMode;
			}
			
			// Call the base constructor
			var pAttributes:Attributes = new Attributes(0, 0, nWidth, nHeight);
			super(screen, SEQUENCER, pAttributes);
			
			// Get references to our header and body
			m_pSequencerHeader = findViewById("sequencer_header") as SequencerHeader;
			m_pSequencerBody = findViewById("sequencer_body") as SequencerBody;
			
			// Pass the widths to the body
			m_pSequencerBody.SetWidths(nUnitOperationWidth, nButtonSkinWidth);
			
			// Add event listeners
			m_pSequencerHeader.addEventListener(ButtonEvent.CLICK, OnButtonClick);
			m_pSequencerBody.addEventListener(SelectionEvent.CHANGE, OnSelectionChange);
		}
		
		/***
		 * Member functions
		 **/

		// Override the layout function to adjust the size
		public override function layout(attributes:Attributes):void
		{
			// Set our width and height to that of the container
			if (parent is Form)
			{
				attributes.width = (parent as Form).attributes.width;
				attributes.height = (parent as Form).attributes.height;
			}
			
			// Call the base implementation
			super.layout(attributes);
		}

		// Add a skin
		protected function AddSkin(pClass:Class):MovieClip
		{
			var pMovieClip:MovieClip = new pClass() as MovieClip;
			addChild(pMovieClip);
			return pMovieClip;
		}

		// Called when the underlying sequence or component changes
		public function UpdateSequence(pSequence:Sequence):void
		{
			// Update the header and body
			m_pSequencerHeader.UpdateSequence(pSequence);
			m_pSequencerBody.UpdateSequence(pSequence);
		}
		
		// Called when the underlying component changes
		public function UpdateSelectedComponent(nComponentID:int):void
		{
			// Update the header and body
			m_pSequencerHeader.UpdateSelectedComponent(nComponentID);
			m_pSequencerBody.UpdateSelectedComponent(nComponentID);
		}

		// Called when a button is clicked
		protected function OnButtonClick(event:ButtonEvent):void
		{
			// Pass the event to anyone listening
			dispatchEvent(new ButtonEvent(event.button));
		}

		// Called when the grid selection changes
		protected function OnSelectionChange(event:SelectionEvent):void
		{
			// Pass the event to anyone listening
			dispatchEvent(new SelectionEvent(event.selectionID));
		}

		/***
		 * Member variables
		 **/
		
		// Sequencer XML
		protected static const SEQUENCER:XML = 
			<rows heights="23%,77%" gapV="0">
				<sequencerheader id="sequencer_header" />
				<sequencerbody id="sequencer_body"
					unitoperationfontface="GothamBold" unitoperationfontsize="8"
					unitoperationenabledtextcolor={Styling.TEXT_GRAY2} unitoperationdisabledtextcolor={Styling.TEXT_GRAY7} 
					unitoperationactivetextcolor={Styling.TEXT_BLUE1} unitoperationpressedtextcolor={Styling.TEXT_WHITE} 
					notefontface="GothamBold" notefontsize="11" noteenabledtextcolor={Styling.TEXT_GRAY2} 
					notedisabledtextcolor={Styling.TEXT_GRAY7} noteactivetextcolor={Styling.TEXT_BLUE1} 
					numberfontface="GothamBold" numberfontsize="12" numberenabledtextcolor={Styling.TEXT_GRAY2} 
					numberdisabledtextcolor={Styling.TEXT_GRAY2} numberactivetextcolor={Styling.TEXT_WHITE} 
					numberactivebackgroundcolor={Styling.SCROLLER_SELECTED} />
			</rows>;
		
		// Mode
		protected var m_sMode:String = "";
		
		// Components
		protected var m_pBackgroundSkin:MovieClip;
		protected var m_pSequencerHeader:SequencerHeader;
		protected var m_pSequencerBody:SequencerBody;
		
		// Constants
		public static var VISIBLE_COLUMN_COUNT:int = 9;
		public static var BUTTON_GAP:int = 20;
	}
}
