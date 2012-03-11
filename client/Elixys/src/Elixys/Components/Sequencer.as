package Elixys.Components
{
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
		
		public function Sequencer(screen:Sprite, xml:XML, attributes:Attributes)
		{
			// Determine our current width and height
			var nWidth:int = Form.FindWidth(screen);
			var nHeight:int = Form.FindHeight(screen);

			// Add the background skin
			m_pBackgroundSkin = AddSkin(sequencer_windowBackground);
			m_pBackgroundSkin.width = nWidth;
			m_pBackgroundSkin.height = nHeight;

			// Call the base constructor
			var pAttributes:Attributes = new Attributes(0, 0, nWidth, nHeight);
			super(screen, SEQUENCER, pAttributes);
			
			// Get references to our header and body
			m_pSequencerHeader = findViewById("sequencer_header") as SequencerHeader;
			m_pSequencerBody = findViewById("sequencer_body") as SequencerBody;
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

		// Called when the underlying sequence changes
		public function UpdateSequence(nComponentID:uint, pSequence:Sequence):void
		{
			// Update the body
			m_pSequencerBody.UpdateBody(nComponentID, pSequence);
		}
		
		// Called when the underlying component changes
		public function UpdateComponent(pComponent:ComponentBase):void
		{
			trace("Sequencer::UpdateComponent");
		}

		/***
		 * Member variables
		 **/
		
		// Sequencer XML
		protected static const SEQUENCER:XML = 
			<rows heights="23%,77%" gapV="0">
				<sequencerheader id="sequencer_header" />
				<sequencerbody id="sequencer_body" />
			</rows>;
		
		// Components
		protected var m_pBackgroundSkin:MovieClip;
		protected var m_pSequencerHeader:SequencerHeader;
		protected var m_pSequencerBody:SequencerBody;
		
		// Constants
		public static var VISIBLE_COLUMN_COUNT:int = 9;
	}
}
