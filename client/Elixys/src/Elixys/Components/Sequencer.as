package Elixys.Components
{
	import Elixys.Assets.Styling;
	import Elixys.Events.ButtonEvent;
	import Elixys.Events.SelectionEvent;
	import Elixys.Extended.Form;
	import Elixys.JSON.Components.ComponentBase;
	import Elixys.JSON.State.Sequence;
	
	import com.danielfreeman.madcomponents.*;
	
	import flash.display.Sprite;
	import flash.events.MouseEvent;
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
			m_pBackgroundSkin = Utils.AddSkin(sequencer_windowBackground, true, this, nWidth, nHeight);

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
			
			// Pass the widths and sequencer reference to the body
			m_pSequencerBody.SetWidths(nUnitOperationWidth, nButtonSkinWidth);
			m_pSequencerBody.SetSequencer(this);
			
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
		
		// Called to start dragging a new unit operation
		public function StartDraggingNew(pDragTarget:Sprite, sDraggingOperation:String):void
		{
			// Remember the operation and clear the other variables
			m_sDraggingOperation = sDraggingOperation;
			m_nDraggingID = -1;
			m_pDragTargetUpSkin = null;
			m_pDragTargetDeleteSkin = null;
			
			// Start dragging
			StartDragging(pDragTarget);
		}

		// Called to start dragging an existing unit operation
		public function StartDraggingExisting(pDragTarget:Sprite, nDraggingID:int, pUpSkin:Sprite, pDeleteSkin:Sprite):void
		{
			// Remember the ID and skins and clear the operation
			m_nDraggingID = nDraggingID;
			m_pDragTargetUpSkin = pUpSkin;
			m_pDragTargetDeleteSkin = pDeleteSkin;
			m_sDraggingOperation = "";
			
			// Start dragging
			StartDragging(pDragTarget);
		}
		
		// Internal start dragging function
		protected function StartDragging(pDragTarget:Sprite):void
		{
			// Delete any existing drag target
			if (m_pDragTarget != null)
			{
				stage.removeChild(m_pDragTarget);
				m_pDragTarget = null;
			}
			
			// Start dragging
			m_pDragTarget = pDragTarget;
			m_pDragTarget.x = stage.mouseX - (m_pDragTarget.width / 2);
			m_pDragTarget.y = stage.mouseY - (m_pDragTarget.height / 2);
			m_pDragTarget.startDrag();
			stage.addEventListener(MouseEvent.MOUSE_MOVE, OnDragMouseMove);
			stage.addEventListener(MouseEvent.MOUSE_UP, OnDragMouseUp);
		}
		
		// Called when the user moves the mouse while dragging
		protected function OnDragMouseMove(event:MouseEvent):void
		{
			// Move the drag target
			m_pDragTarget.x = stage.mouseX - (m_pDragTarget.width / 2);
			m_pDragTarget.y = stage.mouseY - (m_pDragTarget.height / 2);
			
			// Check if we are dragging a new or existing unit operation
			if (m_nDraggingID != -1)
			{
				// We are dragging an existing unit operation.  Hit test the header first to see if the user is trying
				// to delete the operation
				if (m_pSequencerHeader.DragHitTest(m_pDragTarget))
				{
					// Yes, so show the delete skin
					if (m_pDragTargetUpSkin.visible)
					{
						m_pDragTargetDeleteSkin.visible = true;
						m_pDragTargetUpSkin.visible = false;
					}
					
					// Hide any opening in the sequencer body
					m_pSequencerBody.DragHitTest(null);
				}
				else
				{
					// No, so show the up skin
					if (m_pDragTargetDeleteSkin.visible)
					{
						m_pDragTargetUpSkin.visible = true;
						m_pDragTargetDeleteSkin.visible = false;
					}
					
					// Hit test the sequencer body
					m_pSequencerBody.DragHitTest(m_pDragTarget);
				}
			}
			else
			{
				// We are dragging an new unit operation.  Hit test the sequencer body
				m_pSequencerBody.DragHitTest(m_pDragTarget);
			}
		}
		
		// Called when the user releases the mouse button while dragging
		protected function OnDragMouseUp(event:MouseEvent):void
		{
			// Remove the event listeners
			stage.removeEventListener(MouseEvent.MOUSE_MOVE, OnDragMouseMove);
			stage.removeEventListener(MouseEvent.MOUSE_UP, OnDragMouseUp);
			
			// Check if we are dragging a new or existing unit operation
			if (m_nDraggingID != -1)
			{
				// We are dragging an existing unit operation.  Hit test the header first to see if the user is trying
				// to delete the operation
				if (m_pSequencerHeader.DragHitTest(m_pDragTarget))
				{
					// Yes, so delete the unit operation
					m_pSequencerBody.DropOnDelete();
				}
				else
				{
					// No, so give the sequencer body a chance to reorder the existing unit operation
					m_pSequencerBody.DropExisting(m_pDragTarget);
				}
			}
			else
			{
				// We are dragging an new unit operation.  Give the sequencer body a chance to insert
				// the new unit operation
				m_pSequencerBody.DropNew(m_pDragTarget, m_sDraggingOperation);
			}
			
			// Delete the drag target
			if (m_pDragTarget != null)
			{
				stage.removeChild(m_pDragTarget);
				m_pDragTarget = null;
			}
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
		protected var m_pBackgroundSkin:Sprite;
		protected var m_pSequencerHeader:SequencerHeader;
		protected var m_pSequencerBody:SequencerBody;
		
		// Drag-and-drop variables
		protected var m_pDragTarget:Sprite;
		protected var m_nDraggingID:int = -1;
		protected var m_pDragTargetUpSkin:Sprite;
		protected var m_pDragTargetDeleteSkin:Sprite;
		protected var m_sDraggingOperation:String = "";

		// Constants
		public static var VISIBLE_COLUMN_COUNT:int = 9;
		public static var BUTTON_GAP:int = 20;
	}
}
