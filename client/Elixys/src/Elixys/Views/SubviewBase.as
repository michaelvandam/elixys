package Elixys.Views
{
	import Elixys.Events.HTTPRequestEvent;
	import Elixys.HTTP.HTTPConnection;
	import Elixys.HTTP.HTTPRequest;
	import Elixys.Objects.*;
	
	import flash.events.EventDispatcher;
	import flash.events.MouseEvent;
	import flash.utils.ByteArray;
	
	import mx.containers.ViewStack;
	import mx.events.FlexEvent;
	
	import spark.components.Button;
	import spark.components.HGroup;
	import spark.components.Label;
	import spark.components.List;
	import spark.components.VGroup;

	public class SubviewBase extends ViewBase
	{
		/**
		 * Member functions
		 **/

		// Constructor
		public function SubviewBase()
		{
			// Call the base constructor
			super();
		}

		// Set view mode
		public function SetViewMode(sViewMode:String):void
		{
			// Set the visibility of the components in the derived class
			m_sViewMode = sViewMode;
			if (m_pViewGroup != null)
			{
				m_pViewGroup.visible = (m_sViewMode == VIEWMODE);
				m_pViewGroup.includeInLayout = (m_sViewMode == VIEWMODE);
			}
			if (m_pEditGroup != null)
			{
				m_pEditGroup.visible = (m_sViewMode == EDITMODE);
				m_pEditGroup.includeInLayout = (m_sViewMode == EDITMODE);
			}
			if (m_pRunGroup != null)
			{
				m_pRunGroup.visible = (m_sViewMode == RUNMODE);
				m_pRunGroup.includeInLayout = (m_sViewMode == RUNMODE);
			}
		}

		/***
		 * Member variables
		 **/
		
		// View modes
		static public var VIEWMODE:String = "View";
		static public var EDITMODE:String = "Edit";
		static public var RUNMODE:String = "Run";

		// Current view mode
		public var m_sViewMode:String;

		// Pointers to the UI component of the derived class
		protected var m_pViewGroup:VGroup = null;
		protected var m_pEditGroup:VGroup = null;
		protected var m_pRunGroup:VGroup = null;
	}
}
