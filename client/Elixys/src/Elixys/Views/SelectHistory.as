package Elixys.Views
{
	import Elixys.Assets.Styling;
	import Elixys.Components.NavigationBar;
	import Elixys.Components.Screen;
	import Elixys.Extended.Form;
	import Elixys.JSON.State.State;
	import Elixys.JSON.State.StateSelect;
	
	import com.danielfreeman.madcomponents.*;
	
	import flash.display.Sprite;
	import flash.utils.*;
	
	// This select history view is an extension of the Screen class
	public class SelectHistory extends Screen
	{
		/***
		 * Construction
		 **/
		
		public function SelectHistory(screen:Sprite, pElixys:Elixys, xml:XML, attributes:Attributes = null, row:Boolean = false, inGroup:Boolean = false)
		{
			// Call the base constructor
			super(screen, pElixys, SELECTHISTORY, attributes, row, inGroup);
		}

		/***
		 * Loading functions
		 **/
		
		// Loads the next child component and return true or returns false if the load is complete
		public override function LoadNext():Boolean
		{
			if (m_nChildrenLoaded < LOAD_STEPS)
			{
				// Step 1 is loading the navigation bar
				if (m_nChildrenLoaded == 0)
				{
					LoadNavigationBar();
				}
				
				// Step 2 is loading the sequence grid
				if (m_nChildrenLoaded == 1)
				{
				}
				
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
		protected function LoadNavigationBar():void
		{
			// Get the navigation bar container
			var pContainer:Form = Form(UI.findViewById("selecthistory_navigationbar_container"));
			
			// Load the navigation bar
			var pAttributes:Attributes = new Attributes(0, 0, width, height);
			m_pNavigationBar = new NavigationBar(pContainer, NAVIGATION, pAttributes);
			
			// Append the navigation bar to the XML and refresh
			pContainer.xml.appendChild(NAVIGATION);
			pContainer.AppendChild(m_pNavigationBar);
			layout(attributes);
		}
		
		/***
		 * Member functions
		 **/
		
		// Updates the state
		public override function UpdateState(pState:State):void
		{
			// Update the navigation bar buttons
			//var pStateSelect:StateSelect = new StateSelect(null, pState);
			//m_pNavigationBar.UpdateButtons(pStateSelect.NavigationButtons);
		}
		
		/***
		 * Member variables
		 **/

		// Select saved screen XML
		protected static const SELECTHISTORY:XML = 
			<frame background={Styling.APPLICATION_BACKGROUND} alignH="fill" alignV="fill">
				<rows gapV="0" border="false" heights="18%,64%" alignH="fill" alignV="fill">
					<frame id="selecthistory_navigationbar_container" alignV="fill" alignH="fill" />
					<frame alignH="fill" alignV="fill" />
				</rows>
			</frame>;
		
		// Navigation bar XML
		protected static const NAVIGATION:XML =
			<navigationbar alignH="fill" alignV="fill" skin={getQualifiedClassName(blueNavigationBar_mc)}>
				<navigationbaroption name="SEQUENCER" foregroundskinheightpercent="35" fontSize="12" fontFace="GothamMedium"
						enabledTextColor={Styling.TEXT_WHITE} disabledTextColor={Styling.TEXT_GRAY}
						foregroundskinup={getQualifiedClassName(mainNav_sequencer_disabled)}
						foregroundskindown={getQualifiedClassName(mainNav_sequencer_disabled)} 
						foregroundskindisabled={getQualifiedClassName(mainNav_sequencer_disabled)}>
					SEQUENCER
				</navigationbaroption>
				<navigationbaroption name="NEWSEQUENCE" foregroundskinheightpercent="35" fontSize="12" fontFace="GothamMedium"
						enabledTextColor={Styling.TEXT_WHITE} disabledTextColor={Styling.TEXT_GRAY}
						foregroundskinup={getQualifiedClassName(seqListNav_newSequence_up)}
						foregroundskindown={getQualifiedClassName(seqListNav_newSequence_down)} 
						foregroundskindisabled={getQualifiedClassName(seqListNav_newSequence_disabled)}>
					NEW SEQUENCE
				</navigationbaroption>
				<navigationbaroption name="COPYSEQUENCE" foregroundskinheightpercent="35" fontSize="12" fontFace="GothamMedium"
						enabledTextColor={Styling.TEXT_WHITE} disabledTextColor={Styling.TEXT_GRAY}
						foregroundskinup={getQualifiedClassName(seqListNav_copySequence_up)}
						foregroundskindown={getQualifiedClassName(seqListNav_copySequence_down)} 
						foregroundskindisabled={getQualifiedClassName(seqListNav_copySequence_disabled)}>
					COPY SEQUENCE
				</navigationbaroption>
				<navigationbaroption name="VIEWSEQUENCE" foregroundskinheightpercent="35" fontSize="12" fontFace="GothamMedium"
						enabledTextColor={Styling.TEXT_WHITE} disabledTextColor={Styling.TEXT_GRAY}
						foregroundskinup={getQualifiedClassName(seqListNav_viewSequence_up)}
						foregroundskindown={getQualifiedClassName(seqListNav_viewSequence_down)} 
						foregroundskindisabled={getQualifiedClassName(seqListNav_viewSequence_disabled)}>
					VIEW SEQUENCE
				</navigationbaroption>
				<navigationbaroption name="EDITSEQUENCE" foregroundskinheightpercent="35" fontSize="12" fontFace="GothamMedium"
						enabledTextColor={Styling.TEXT_WHITE} disabledTextColor={Styling.TEXT_GRAY}
						foregroundskinup={getQualifiedClassName(seqListNav_editSequence_up)}
						foregroundskindown={getQualifiedClassName(seqListNav_editSequence_down)} 
						foregroundskindisabled={getQualifiedClassName(seqListNav_editSequence_disabled)}>
					EDIT SEQUENCE
				</navigationbaroption>
				<navigationbaroption name="RUNSEQUENCE" foregroundskinheightpercent="35" fontSize="12" fontFace="GothamMedium"
						enabledTextColor={Styling.TEXT_WHITE} disabledTextColor={Styling.TEXT_GRAY}
						foregroundskinup={getQualifiedClassName(seqListNav_runSequence_up)}
						foregroundskindown={getQualifiedClassName(seqListNav_runSequence_down)}
						foregroundskindisabled={getQualifiedClassName(seqListNav_runSequence_disabled)}>
					RUN SEQUENCE
				</navigationbaroption>
				<navigationbaroption name="DELETESEQUENCE" foregroundskinheightpercent="35" fontSize="12" fontFace="GothamMedium"
						enabledTextColor={Styling.TEXT_WHITE} disabledTextColor={Styling.TEXT_GRAY}
						foregroundskinup={getQualifiedClassName(seqListNav_deleteSequence_up)}
						foregroundskindown={getQualifiedClassName(seqListNav_deleteSequence_down)} 
						foregroundskindisabled={getQualifiedClassName(seqListNav_deleteSequence_disabled)}>
					DELETE SEQUENCE
				</navigationbaroption>
			</navigationbar>;
		
		// Number of steps required to load this object
		public static var LOAD_STEPS:uint = 2;
		
		// The current step
		protected var m_nChildrenLoaded:uint = 0;
		
		// Screen components
		protected var m_pNavigationBar:NavigationBar;
	}
}
