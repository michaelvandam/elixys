package Elixys.Views
{
	import Elixys.Assets.*;
	import Elixys.Components.DropdownList;
	import Elixys.Events.ButtonEvent;
	import Elixys.Events.DropdownEvent;
	import Elixys.Extended.Form;
	import Elixys.JSON.State.Reagents;
	import Elixys.JSON.State.State;
	import Elixys.JSON.State.StateSequence;
	import Elixys.JSON.State.Tab;
	import Elixys.Subviews.SubviewBase;
	
	import com.danielfreeman.madcomponents.*;
	
	import flash.display.Sprite;
	import flash.events.Event;
	import flash.events.EventDispatcher;
	import flash.utils.*;
	
	// This sequence edit screen is an extension of the base sequence class
	public class SequenceEdit extends SequenceBase
	{
		/***
		 * Construction
		 **/
		
		public function SequenceEdit(screen:Sprite, pElixys:Elixys, xml:XML, attributes:Attributes = null, row:Boolean = false, inGroup:Boolean = false)
		{
			// Call the base constructor
			super(screen, pElixys, SEQUENCEEDIT, attributes, row, inGroup);
			
			// Set our mode
			m_sMode = Constants.EDIT;
		}

		/***
		 * Loading functions
		 **/
		
		// Loads the next child component and return true or returns false if the load is complete
		public override function LoadNext():Boolean
		{
			// Load the edit children first
			if (m_nChildrenLoaded < EDIT_LOAD_STEPS)
			{
				// Step 1 is loading the navigation bar
				if (m_nChildrenLoaded == 0)
				{
					LoadNavigationBar("sequenceedit_navigationbar_container", NAVIGATION);
				}

				// Step 2 is loading the tab bar
				if (m_nChildrenLoaded == 1)
				{
					m_pTabs = new Array();
					m_pTabs.push(Tab.CreateTab("CASSETTES", "CASSETTES"));
					m_pTabs.push(Tab.CreateTab("TOOLS", "TOOLS"));
					LoadTabBar("sequenceedit_tabbar_container", m_pTabs, "CASSETTES");
				}
				
				// Step 3 is loading the tools component
				if (m_nChildrenLoaded == 2)
				{
					LoadSequenceTools("sequenceedit_cassettestools_container");
				}

				// Step 4 is loading the cassettes component
				if (m_nChildrenLoaded == 3)
				{
					LoadSequenceCassettes("sequenceedit_cassettestools_container");
				}
				
				// Step 5 is loading the sequencer
				if (m_nChildrenLoaded == 4)
				{
					LoadSequencer("sequenceedit_sequencer_container", SEQUENCER);
				}
				
				// Increment and return
				++m_nChildrenLoaded;
				return true;
			}

			// Call the base function to load the base children
			return LoadNextBase(LOAD_STEPS);
		}

		/***
		 * Member functions
		 **/
		
		// Updates the state
		public override function UpdateState(pState:State):void
		{
			// Call the base handler
			super.UpdateState(pState);
		}
		
		// Updates the reagent list
		public override function UpdateReagents(pReagents:Reagents):void
		{
			for (var nIndex:int = 0; nIndex < m_pSubviews.length; ++nIndex)
			{
				(m_pSubviews[nIndex] as SubviewBase).UpdateReagents(pReagents);
			}
		}
		
		// Called when a tab on the tab bar is clicked
		protected override function OnTabClick(event:ButtonEvent):void
		{
			// Change the selected tab and the visible component
			if (event.button == "CASSETTES")
			{
				m_pTabBar.UpdateTabs(m_pTabs, "CASSETTES");
				m_pSequenceCassettes.parent.setChildIndex(m_pSequenceCassettes, m_pSequenceCassettes.parent.numChildren - 1);
			}
			else
			{
				m_pTabBar.UpdateTabs(m_pTabs, "TOOLS");
				m_pSequenceTools.parent.setChildIndex(m_pSequenceTools, m_pSequenceTools.parent.numChildren - 1);
			}
		}

		// Shows the dropdown list
		public function ShowDropdownList(pValues:Array, sCurrentValue:String, pParent:Form, pEventListener:EventDispatcher, pData:Array = null):void
		{
			// Creating the dropdown list
			if (!m_pDropdownList)
			{
				m_pDropdownList = new DropdownList(pParent, pParent.attributes);
				m_pDropdownList.addEventListener(DropdownEvent.ITEMSELECTED, OnDropdownEvent);
				m_pDropdownList.addEventListener(DropdownEvent.LISTHIDDEN, OnDropdownEvent);
				m_pDropdownList.visible = true;
			}

			// Assign the dropdown to the parent
			if ((m_pDropdownList.parent == null) || (m_pDropdownList.parent != pParent))
			{
				if (m_pDropdownList.parent != null)
				{
					m_pDropdownList.parent.removeChild(m_pDropdownList);
				}
				pParent.addChild(m_pDropdownList);
				m_pDropdownList.visible = true;
			}
			
			// Remember the current event listener
			m_pDropdownEventListener = pEventListener;

			// Pass the current value and array
			m_pDropdownList.SetList(pValues, sCurrentValue, pData);
		}

		// Hides the dropdown list
		public function HideDropdownList():void
		{
			if (m_pDropdownList)
			{
				// Remove the dropdown from the parent
				if (m_pDropdownList.parent)
				{
					m_pDropdownList.visible = false;
					m_pDropdownList.parent.removeChild(m_pDropdownList);
				}
			
				// Clear the current event listener
				m_pDropdownEventListener = null;
			}
		}
		
		// Called when the dropdown emits and event
		protected function OnDropdownEvent(event:DropdownEvent):void
		{
			// Pass the event to our listener
			m_pDropdownEventListener.dispatchEvent(event.Copy());
		}

		/***
		 * Member variables
		 **/

		// Sequence edit XML
		protected static const SEQUENCEEDIT:XML = 
			<frame background={Styling.APPLICATION_BACKGROUND} alignH="fill" alignV="fill">
				<rows gapV="0" border="false" heights="18%,61%,21%" alignH="fill" alignV="fill">
					<frame id="sequenceedit_navigationbar_container" alignV="fill" alignH="fill" />
					<rows heights="8%,3%,89%" gapV="0" alignV="fill" alignH="fill">
						<frame id="sequence_title_container" />
						<frame />
						<columns widths="20,34%,4,66%" gapH="0" alignV="fill" alignH="fill">
							<frame />
							<rows heights="10%,90%" gapV="0" alignV="fill" alignH="fill">
								<frame id="sequenceedit_tabbar_container" />
								<frame id="sequenceedit_cassettestools_container" />
							</rows>
							<rows heights="9%,85%,6%" gapV="0" alignV="fill" alignH="fill">
								<frame />
								<frame background={Styling.TABBAR_LINE} />
							</rows>
							<frame id="unitoperation_container" />
						</columns>
					</rows>
					<frame id="sequenceedit_sequencer_container" alignV="fill" alignH="fill" />
				</rows>
			</frame>;
		
		// Navigation bar XML
		protected static const NAVIGATION:XML =
			<navigationbar alignH="fill" alignV="fill" skin={getQualifiedClassName(blueNavigationBar_mc)} rightpadding="20">
				<navigationbaroption name="SEQUENCER" backgroundskinheightpercent="72" foregroundskinheightpercent="30"
						fontSize="12" fontFace="GothamMedium"
						enabledTextColor={Styling.TEXT_GRAY1} disabledTextColor={Styling.TEXT_GRAY1}
						backgroundskinup={getQualifiedClassName(mainNav_activeBtnOutline_up)}
						backgroundskindown={getQualifiedClassName(mainNav_activeBtnOutline_down)}
						backgroundskindisabled={getQualifiedClassName(mainNav_activeBtnOutline_up)}
						foregroundskinup={getQualifiedClassName(mainNav_sequencer_active)}
						foregroundskindown={getQualifiedClassName(mainNav_sequencer_down)} 
						foregroundskindisabled={getQualifiedClassName(mainNav_sequencer_disabled)}>
					SEQUENCER
				</navigationbaroption>
				<navigationbaroption name="VIEWSEQUENCE" foregroundskinheightpercent="30" fontSize="12" fontFace="GothamMedium"
						enabledTextColor={Styling.TEXT_WHITE} disabledTextColor={Styling.TEXT_BLUE3}
						foregroundskinup={getQualifiedClassName(seqListNav_viewSequence_up)}
						foregroundskindown={getQualifiedClassName(seqListNav_viewSequence_down)} 
						foregroundskindisabled={getQualifiedClassName(seqListNav_viewSequence_disabled)}>
					VIEW SEQUENCE
				</navigationbaroption>
				<navigationbaroption name="RUNSEQUENCE" foregroundskinheightpercent="30" fontSize="12" fontFace="GothamMedium"
						enabledTextColor={Styling.TEXT_WHITE} disabledTextColor={Styling.TEXT_BLUE3}
						foregroundskinup={getQualifiedClassName(seqListNav_runSequence_up)}
						foregroundskindown={getQualifiedClassName(seqListNav_runSequence_down)}
						foregroundskindisabled={getQualifiedClassName(seqListNav_runSequence_disabled)}>
					RUN SEQUENCE
				</navigationbaroption>
				<navigationbaroption name="RUNSEQUENCEHERE" foregroundskinheightpercent="30" fontSize="12" fontFace="GothamMedium"
						enabledTextColor={Styling.TEXT_WHITE} disabledTextColor={Styling.TEXT_BLUE3}
						foregroundskinup={getQualifiedClassName(seqListNav_runSequence_up)}
						foregroundskindown={getQualifiedClassName(seqListNav_runSequence_down)}
						foregroundskindisabled={getQualifiedClassName(seqListNav_runSequence_disabled)}>
					RUN FROM HERE
				</navigationbaroption>
				<navigationbaroption blank="true" />
				<navigationbaroption blank="true" />
				<navigationbaroption blank="true" />
			</navigationbar>;
		
		// Sequencer XML
		protected static const SEQUENCER:XML =
			<sequencer mode={Constants.EDIT} alignH="fill" alignV="fill"/>;
		
		// Tabs
		protected var m_pTabs:Array;
		
		// Number of steps required to load this object
		public static var EDIT_LOAD_STEPS:uint = 5;
		public static var LOAD_STEPS:uint = SequenceBase.BASE_LOAD_STEPS + EDIT_LOAD_STEPS;
		
		// View components
		protected var m_pDropdownList:DropdownList;
		protected var m_pDropdownEventListener:EventDispatcher;
	}
}
