package Elixys.Views
{
	import Elixys.Components.NavigationBar;
	import Elixys.Components.Screen;
	import Elixys.Components.Sequencer;
	import Elixys.Events.ButtonEvent;
	import Elixys.Events.SelectionEvent;
	import Elixys.Extended.Form;
	import Elixys.JSON.Components.ComponentBase;
	import Elixys.JSON.Post.PostSequence;
	import Elixys.JSON.State.Sequence;
	import Elixys.JSON.State.State;
	import Elixys.JSON.State.StateSequence;
	
	import com.danielfreeman.madcomponents.*;
	
	import flash.display.Sprite;
	
	// This base sequence view is an extension of the screen class
	public class SequenceBase extends Screen
	{
		/***
		 * Construction
		 **/
		
		public function SequenceBase(screen:Sprite, pElixys:Elixys, xml:XML, attributes:Attributes = null, row:Boolean = false, inGroup:Boolean = false)
		{
			// Call the base constructor
			super(screen, pElixys, xml, attributes, row, inGroup);
		}
		
		/***
		 * Loading functions
		 **/
		
		// Loads the next child component and return true or returns false if the load is complete
		public function LoadNextBase(nLoadSteps:uint):Boolean
		{
			if (m_nChildrenLoaded < nLoadSteps)
			{
				// Increment and return
				++m_nChildrenLoaded;
				return true;
			}
			else
			{
				// Load complete
				return false;
			}
		}
		
		// Load the navigation bar
		protected function LoadNavigationBar(sContainerID:String, pNavigationXML:XML):void
		{
			// Get the navigation bar container
			var pContainer:Form = Form(findViewById(sContainerID));
			
			// Load the navigation bar
			var pAttributes:Attributes = new Attributes(0, 0, width, height);
			m_pNavigationBar = new NavigationBar(pContainer, pNavigationXML, pAttributes);
			m_pNavigationBar.addEventListener(ButtonEvent.CLICK, OnButtonClick);
			
			// Append the navigation bar to the XML and refresh
			pContainer.xml.appendChild(pNavigationXML);
			pContainer.AppendChild(m_pNavigationBar);
			layout(attributes);
		}

		// Load the sequencer
		protected function LoadSequencer(sContainerID:String, pSequencerXML:XML):void
		{
			// Get the sequencer container
			var pContainer:Form = Form(findViewById(sContainerID));
			
			// Load the sequencer
			var pAttributes:Attributes = new Attributes(0, 0, width, height);
			m_pSequencer = new Sequencer(pContainer, pSequencerXML, pAttributes);
			m_pSequencer.addEventListener(SelectionEvent.CHANGE, OnSelectionChange);
			m_pSequencer.addEventListener(ButtonEvent.CLICK, OnButtonClick);
			
			// Append the navigation bar to the XML and refresh
			pContainer.xml.appendChild(pSequencerXML);
			pContainer.AppendChild(m_pSequencer);
			layout(attributes);
		}

		/***
		 * Member functions
		 **/

		// Updates the state
		public override function UpdateState(pState:State):void
		{
			// Check what has changed since our last update
			var pStateSequence:StateSequence = new StateSequence(StateSequence.VIEWTYPE, null, pState);
			var bButtonsChanged:Boolean = true, bComponentChanged:Boolean = true;
			if (m_pStateSequence != null)
			{
				bButtonsChanged = !Elixys.JSON.State.Button.CompareButtonArrays(pStateSequence.Buttons, m_pStateSequence.Buttons);
				bComponentChanged = (pStateSequence.ClientState.ComponentID != m_pStateSequence.ClientState.ComponentID);
			}
			
			// Update the navigation bar buttons
			if (bButtonsChanged)
			{
				m_pNavigationBar.UpdateButtons(pStateSequence.Buttons);
			}

			// Update the sequencer
			if (bComponentChanged)
			{
				m_pSequencer.UpdateSelectedComponent(pStateSequence.ClientState.ComponentID);
			}
			
			// Remember the new state
			m_pStateSequence = pStateSequence;
			
			// Fetch the sequence and component from the server
			DoGet("/Elixys/sequence/" + pState.ClientState.SequenceID);
			DoGet("/Elixys/sequence/" + pState.ClientState.SequenceID + "/component/" + pState.ClientState.ComponentID);
		}

		// Updates the sequence
		public override function UpdateSequence(pSequence:Sequence):void
		{
			// Check if the sequence has changed
			var bSequenceChanged:Boolean = true;
			if (m_pSequence != null)
			{
				bSequenceChanged = !Sequence.CompareSequences(pSequence, m_pSequence);
			}
			
			// Update the sequencer
			if (bSequenceChanged)
			{
				m_pSequencer.UpdateSequence(pSequence);
			}
			
			// Remember the new sequence
			m_pSequence = pSequence;
		}
		
		// Updates the component
		public override function UpdateComponent(pComponent:ComponentBase):void
		{
			// Check if the component has changed
			var bComponentChanged:Boolean = true;
			if (m_pComponent != null)
			{
				bComponentChanged = !ComponentBase.CompareComponents(pComponent, m_pComponent);
			}
			
			// Remember the new component
			m_pComponent = pComponent;
		}

		// Called when a button on the navigation bar is clicked
		protected function OnButtonClick(event:ButtonEvent):void
		{
			// Send a button click to the server
			var pPostSequence:PostSequence = new PostSequence();
			pPostSequence.TargetID = event.button;
			DoPost(pPostSequence, m_sPostString);
		}

		// Called when the unit operation selection changes
		protected function OnSelectionChange(event:SelectionEvent):void
		{
			// Send the unit operation click to the server
			var pPostSequence:PostSequence = new PostSequence();
			pPostSequence.TargetID = event.selectionID.toString();
			DoPost(pPostSequence, m_sPostString);
		}

		/***
		 * Member variables
		 **/
		
		// Number of steps required to load this object
		public static var BASE_LOAD_STEPS:uint = 18;
		
		// The current step
		protected var m_nChildrenLoaded:uint = 0;

		// Post string
		protected var m_sPostString:String = "";
		
		// Currently displayed state, sequence and component
		protected var m_pStateSequence:StateSequence;
		protected var m_pSequence:Sequence;
		protected var m_pComponent:ComponentBase;
		
		// Screen components
		protected var m_pNavigationBar:NavigationBar;
		protected var m_pSequencer:Sequencer;
	}
}
