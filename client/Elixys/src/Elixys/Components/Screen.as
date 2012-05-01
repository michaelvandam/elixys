package Elixys.Components
{
	import Elixys.Events.HTTPRequestEvent;
	import Elixys.Extended.Form;
	import Elixys.HTTP.HTTPRequest;
	import Elixys.JSON.Components.ComponentBase;
	import Elixys.JSON.State.Reagents;
	import Elixys.JSON.State.Sequence;
	import Elixys.JSON.State.State;
	
	import com.danielfreeman.madcomponents.*;
	
	import flash.display.Sprite;
	import flash.utils.ByteArray;
	
	// This screen component is an extension of the Form class
	public class Screen extends Form
	{
		/***
		 * Construction
		 **/
		
		public function Screen(screen:Sprite, pElixys:Elixys, xml:XML, attributes:Attributes = null, row:Boolean = false, inGroup:Boolean = false)
		{
			// Call the base constructor
			super(screen, xml, attributes, row, inGroup);
			
			// Remember the parent
			m_pElixys = pElixys;
		}
		
		/***
		 * Member functions
		 **/
		
		// Loads the next child component.  Return true if loading or false if the load is complete
		public function LoadNext():Boolean
		{
			return false;
		}
		
		// Updates the state
		public function UpdateState(pState:State):void
		{
		}
		
		// Updates the sequence
		public function UpdateSequence(pSequence:Sequence):void
		{
		}

		// Updates the component
		public function UpdateComponent(pComponent:ComponentBase):void
		{
		}

		// Update the reagent list
		public function UpdateReagents(pReagents:Reagents):void
		{
		}

		// Posts the object to the server
		public function DoPost(pPost:Object, sViewName:String):void
		{
			// Convert the request to a byte array
			var pBody:ByteArray = new ByteArray();
			if (pPost != null)
			{
				pBody.writeMultiByte(pPost.toString(), "utf8");
				pBody.position = 0;
			}
			
			// Pass the request up to be sent to the server
			var pHTTPRequest:HTTPRequest = new HTTPRequest();
			pHTTPRequest.m_sMethod = "POST";
			pHTTPRequest.m_sResource = "/Elixys/" + sViewName;
			pHTTPRequest.m_pBody = pBody;
			m_pElixys.dispatchEvent(new HTTPRequestEvent(pHTTPRequest));
		}

		// Gets data from the server
		public function DoGet(sResource:String):void
		{
			// Pass the request up to be sent to the server
			var pHTTPRequest:HTTPRequest = new HTTPRequest();
			pHTTPRequest.m_sMethod = "GET";
			pHTTPRequest.m_sResource = sResource;
			m_pElixys.dispatchEvent(new HTTPRequestEvent(pHTTPRequest));
		}

		/***
		 * Member variables
		 **/
		
		// Main Elixys application
		protected var m_pElixys:Elixys;
	}
}
